
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

combine_prompt = PromptTemplate.from_template("""
You are a research synthesizer. Combine these points into a coherent short report.

Topic: {query}

Sections:
{points}

Report:
""")
llm = ChatOpenAI(model="gpt-4o-mini",temperature=0.2)


def combine_node(state):
    summaries = state.get("summaries", [])
    points = [f"### {s['task']}\n{s['text']}" for s in summaries]

    report = llm.invoke(combine_prompt.format(
        query=state["input"],
        points="\n\n".join(points)
    )).content

    return {"report": report}
