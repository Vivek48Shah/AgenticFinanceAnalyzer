from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
import ast 
import re

llm = ChatOpenAI(model="gpt-4o-mini",temperature=0.2)


planner_prompt = ChatPromptTemplate.from_template(
    """
    You are a financial research planner.

    The user wants to analyze a publicly traded company or stock.

    Break their query down into 4 specific web search tasks that will help:
    1. Get the company’s most recent financials and key metrics (like revenue, EPS, P/E).
    2. Understand sentiment from recent news and expert opinions.
    3. Identify recent events, risks, or controversies.
    4. Capture macro trends or industry comparisons relevant to the company.

    Return ONLY a Python list of 4 strings (one per search task). Do NOT include code blocks.

    User Query: {query}
    """
)


def planner_node(state):
    query = state['input']
    response = llm.invoke(planner_prompt.format(query=query))

    content = response.content.strip()
    if content.startswith("```"):
        content = re.sub(r"```[\s\S]*?\n", "", content)  # Remove ```python or initial block
        content = content.replace("```", "").strip()

    try:
        tasks = ast.literal_eval(content.strip())
        assert isinstance(tasks, list)
    except Exception as e:
        print("[PlannerNode] Failed to parse LLM output:")
        
        raise e

    #print("[Planner] Generated tasks:", tasks)
    return {"tasks": tasks, "input": query}
