import json
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch, TavilyExtract
import re 
tavily_search = TavilySearch(max_results=3,time_range="month",topic="finance",include_domains=[
        "sec.gov",             # official filings
        "reuters.com",         # reliable business reporting
        "bloomberg.com",       # institutional insights
        "finance.yahoo.com",   # mainstream financial coverage
        "investorplace.com",   # rumors + catalysts
        "marketwatch.com"      # broader news and macro coverage
    ],
    exclude_domains=[
        "reddit.com", "fool.com", "quora.com"  # avoid speculative or low-signal content
    ])
tavily_extract = TavilyExtract()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def run_catalyst_agent(task: str, index: int) -> dict:
    company = task.split()[0]
    query = (
    f"{company} confirmed new upcoming events OR regulatory decisions OR lockup expiration OR product launches "
    f"OR institutional investor day OR insider selling OR supply chain announcement")
    

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
You are a hedge fund research analyst. Based on the following text, identify important upcoming **non-routine** events for {company} that may significantly impact the stock price.
{combined_text}
Only include forward-looking events with confirmed or expected **exact dates**. Focus on catalysts such as:

- Regulatory decisions (e.g. SEC, NHTSA, DOJ)
- Lockup expirations or share dilution plans
- Insider selling clusters (e.g. Form 4 filings)
- Major product launches or strategic partnerships
- Executive transitions or investor days
- Government investigations or approvals
- Big contract wins or supply chain shifts

DO NOT include standard quarterly earnings calls unless something **unusual or unexpected** is forecasted (e.g. guidance revision, controversy).

Exclude past events or historical summaries.

Respond ONLY in the following JSON format:

{{
  "events": [
    {{
      "date": "2024-08-15",
      "event": "New battery platform launch",
      "importance": 5,
      "sources": ["https://example.com"]
    }},
    {{
      "date": "2024-09-01",
      "event": "Lockup expiration for insider shares", 
      "importance": 4,
      "sources": ["https://sec.gov/filings/lockup"]
    }}
  ],
  "warnings": [
    "Potential union vote at Giga Berlin in Q3",
    "Ongoing SEC probe may conclude in September"
  ]
}}
"""

    
    response = llm.invoke(prompt).content.strip()
    
    if response.startswith("```"):
        response = response.strip("`")
        response = re.sub(r"^json", "", response, flags=re.IGNORECASE).strip()

    try: 
        events = json.loads(response)
    except:
        events = []

#     print(f"[catalyst_agent] Returning:", {
#     "task": task,
#     "type": "catalyst",
#     "summary": events,
#     "sources": urls
# })
    

    return {
        "task": query,
        "type": "catalyst",
        "summary": events,
        "confidence": "Medium",
        "sources": urls
    }