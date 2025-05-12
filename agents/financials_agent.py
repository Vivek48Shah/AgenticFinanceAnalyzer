import json
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch, TavilyExtract
import re


tavily_search = TavilySearch(
    max_results=5,
    topic="finance",
    include_domains=[
        "sec.gov",             # 10-K / 10-Q filings
        "finance.yahoo.com",   # key stats & summaries
        "bloomberg.com",       # institutional summaries
        "reuters.com",         # analyst summaries
        "marketscreener.com",  # ratios + forecasts
        "marketwatch.com",     # retail investor summaries
    ]
)
tavily_extract = TavilyExtract()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def run_financials_agent(task: str, index: int) -> dict:
    company = task.split()[0]  # crude parse: assumes first word is the company/ticker
    query = (
    f"{company} Q1 2025 earnings OR latest 10-Q filing OR quarterly financial report "
    '"revenue" OR "net income" OR "EPS" OR "PE ratio" OR "EBITDA" '
    "site:sec.gov OR site:finance.yahoo.com OR site:marketscreener.com OR site:bloomberg.com"
)

    search_results = tavily_search.invoke(query)
    urls = [r["url"] for r in search_results["results"]]

    # Extract content from top 2 results
    extraction_result = tavily_extract.invoke({"urls": urls})
    
    extracted_texts = []

    for j, doc in enumerate(extraction_result["results"]):
        raw = doc.get("raw_content", "")
        url = doc.get("url", f"unknown_{j}")
        if not raw:
            continue
        extracted_texts.append(raw)

    combined_text = "\n".join(extracted_texts)

    

    prompt = f"""Analyze the text below to extract financial data for {company} following these rules:
{combined_text}

1. **Required Metrics**:
   - Revenue (USD millions)
   - Net Income (USD millions)
   - EPS (Earnings Per Share)
   - P/E Ratio (Price-to-Earnings)
   - EV/EBITDA (Enterprise Value/EBITDA)

2. **Validation Rules**:
   - Confirm numbers appear in official reports (10-Q/10-K) or earnings releases
   - Cross-check values across multiple sources
   - Flag discrepancies >5% between sources
   - Use most recent quarter available (Q2 2024 > Q1 2024)
   - Note if values are GAAP vs non-GAAP

3. **Format Requirements**:
{{
  "financials": {{
    "revenue": {{
      "value": "12,450",
      "period": "Q2 2024",
      "source": "SEC 10-Q Filing",
      "currency": "USD"
    }},
    "net_income": {{
      "value": "1,890",
      "margin": "15.2%",
      "source": "Earnings Call Transcript"
    }},
    "warning": "3.4% variance in EPS between sources"
  }}
}}"""

    
    response = llm.invoke(prompt).content.strip()
    response = response.strip("```")
    response = re.sub(r"^json", "", response, flags=re.IGNORECASE).strip()
    


    try:
        metrics = json.loads(response)
    except Exception as e:
        metrics = {"error": "Could not parse", "details": str(e)}
        
    
#     print(f"[financials_agent] Returning:", {
#     "task": task,
#     "type": "financial",
#     "summary": metrics,
#     "sources": urls
# })

    return {
        "task": query,
        "type": "financial",
        "summary": metrics,
        "confidence": "Medium",
        "sources": urls
    }