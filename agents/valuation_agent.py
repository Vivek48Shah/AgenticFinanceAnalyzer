from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch, TavilyExtract

tavily_search = TavilySearch(max_results=3,time_range="month", topic="finance")
tavily_extract = TavilyExtract()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def run_valuation_agent(task: str, index: int) -> dict:
    company = task.split()[0]
    query = (
    f"{company} stock valuation OR P/E OR EV/EBITDA OR forward earnings multiple "
    f"OR peer comparison OR industry average valuation OR overvalued OR undervalued "
    f"site:reuters.com OR site:bloomberg.com OR site:finance.yahoo.com OR site:marketwatch.com"
)

    search_results = tavily_search.invoke(query)
    urls = [r["url"] for r in search_results["results"]]

    extraction_result = tavily_extract.invoke({"urls": urls})
    
    extracted_texts = []

    for j, doc in enumerate(extraction_result["results"]):
        raw = doc.get("raw_content", "")
        url = doc.get("url", f"unknown_{j}")
        if not raw:
            continue
        extracted_texts.append(raw)

    combined_text = "\n".join(extracted_texts)
    prompt = f"""
Compare {company}'s valuation to its industry peers using the extracted content below.

Focus on:
- P/E ratio (forward and trailing)
- EV/EBITDA if available
- Market cap vs. competitors

Answer:
- Is {company} trading at a premium or discount vs. peers?
- Is the valuation justified based on growth or risk?

Text:
\"\"\"
{combined_text}
\"\"\"
"""

    try:
        valuation_summary = llm.invoke(prompt).content.strip()
    except:
        valuation_summary = "Could not summarize valuation."
    
    print(f"[valuation_agent] Returning:", {
    "task": task,
    "type": "valuation",
    "summary": valuation_summary,
    "sources": urls
})

    return {
        "task": query,
        "type": "valuation",
        "summary": valuation_summary,
        "confidence": "Medium",
        "sources": urls
    }