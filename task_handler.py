"""
task_handler.py

Handles a single task: web search → extract → clean → summarize → return summary.
"""

from cleaner import clean_extracted_text
from logger import RunLogger
from langchain_openai import ChatOpenAI
from state import summarize_prompt
from langchain_tavily import TavilySearch, TavilyExtract

llm = ChatOpenAI(model="gpt-4o", temperature=0)
tavily_search_tool = TavilySearch(max_results=3,topic="general")
tavily_extract_tool = TavilyExtract()

def task_handler(i, run_logger, llm, summarize_prompt):
    def handle(state):
        if i >= len(state["tasks"]):
            return {"summaries": []}

        task = state["tasks"][i]
        print(f"\n=== Task {i}: {task} ===\n")

        # Search using Tavily
        search_results = tavily_search_tool.invoke(task)
        urls = [result["url"] for result in search_results["results"]]

        # Extract content
        extraction_result = tavily_extract_tool.invoke({"urls": urls})
        
        extracted_texts = []

        for j, doc in enumerate(extraction_result["results"]):
            raw = doc.get("raw_content", "")
            url = doc.get("url", f"unknown_{j}")
            if not raw:
                continue

            # Clean the raw HTML/text
            cleaned_text, removed_matches = clean_extracted_text(
                text=raw,
                query=task,
                url=url,
                doc_id=f"task{i}_doc{j}",
                return_matches=True
            )

            # Log the cleaned task
            run_logger.log_task(
                task_index=i,
                query=task,
                urls=[url],
                removed_matches=removed_matches,
                cleaned_preview=cleaned_text
            )

            extracted_texts.append(cleaned_text)

        # Combine and summarize
        combined_info = "\n".join(extracted_texts)
        summary = llm.invoke(summarize_prompt.format(info=combined_info)).content

        return {
            "summaries": [{"task": task, "text": summary}]
        }

    return handle