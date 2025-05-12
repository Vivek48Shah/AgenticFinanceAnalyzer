import json
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch, TavilyExtract
import re
tavily_search = TavilySearch(max_results=3,time_range="month")
tavily_extract = TavilyExtract()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def run_sentiment_agent(task: str, index: int) -> dict:
    company = task.split()[0]
    query = (
    f"{company} stock analyst sentiment OR market opinion OR price target revisions "
    f"OR downgrade OR upgrade OR analyst rating "
    f"site:marketwatch.com OR site:bloomberg.com OR site:forbes.com OR site:seekingalpha.com"
)

    search_results = tavily_search.invoke(query)
    urls = [r["url"] for r in search_results["results"]]

    texts = []
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
You are a financial research analyst.

Analyze the following news and commentary related to {company} and determine the overall investor sentiment.

Focus on:
- Analyst upgrades/downgrades
- Price target changes
- Fund manager opinions
- Valuation concerns or optimism
- Regulatory impact or earnings commentary

Ignore speculative forums, social media, or blog hype.

Classify the sentiment as one of: **Positive**, **Neutral**, or **Negative**.

Return a JSON object in this format:
{{
  "sentiment": "Positive | Neutral | Negative",
  "summary": "A concise explanation of why, grounded in the content"
}}

Text:
\"\"\"
{combined_text}
\"\"\"
"""

    
    response = llm.invoke(prompt).content.strip()
   

    if response.startswith("```"):
        response = response.strip("`")
        response = re.sub(r"^json", "", response, flags=re.IGNORECASE).strip()
    try:
        sentiment = json.loads(response)
    except:
        sentiment = {"sentiment": "Unknown", "summary": "Could not determine sentiment"}

#     print(f"[sentiment_agent] Returning:", {
#     "task": task,
#     "type": "sentiment",
#     "summary": sentiment,
#     "sources": urls
# })

    return {
        "task": query,
        "type": "sentiment",
        "summary": sentiment,
        "confidence": "Medium",
        "sources": urls
    }