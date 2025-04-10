from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
import ast 
import re

llm = ChatOpenAI(model="gpt-4o-mini",temperature=0.2)


planner_prompt = ChatPromptTemplate.from_template(
    """
    You are a research planner.

    Break down the user's query into 2 to 4 specific web search subtasks.
    Return the output ONLY as a Python list of strings. Do NOT use code blocks.

    Query: {query}
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

    return {"tasks": tasks, "input": query}
