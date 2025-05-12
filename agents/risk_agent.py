from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch, TavilyExtract

tavily_search = TavilySearch(max_results=3,time_range="month")
tavily_extract = TavilyExtract()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def run_risk_agent(task: str, index: int) -> dict:
    company = task.split()[0]
    query = f"{company} risks lawsuits regulatory controversy macroeconomic"

    search_results = tavily_search.invoke(query)
    urls = [r["url"] for r in search_results["results"]]

    # Extract content
    extraction_result = tavily_extract.invoke({"urls": urls})
    
    extracted_texts = []

    for j, doc in enumerate(extraction_result["results"]):
        raw = doc.get("raw_content", "")
        url = doc.get("url", f"unknown_{j}")
        if not raw:
            continue
        extracted_texts.append(raw)

    combined_text = "\n".join(extracted_texts)
    prompt = (
        f"Summarize the major risks facing {company}. Include lawsuits, regulations, or economic challenges. "
        f"Return as a bullet-point list.\n\n{combined_text}"
    )

    try:
        risk_summary = llm.invoke(prompt).content.strip()
    except:
        risk_summary = "Could not identify risks."
    
    print(f"[risk_agent] Returning:", {
    "task": task,
    "type": "risk",
    "summary": risk_summary,
    "sources": urls
})

    return {
        "task": query,
        "type": "risk",
        "summary": risk_summary,
        "confidence": "Medium",
        "sources": urls
    }