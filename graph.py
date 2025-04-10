from langgraph.graph import StateGraph, END
from state import GraphState
from planner import planner_node
from combine import combine_node
from task_handler import task_handler
from langchain_core.runnables import RunnableLambda


def build_graph(run_logger, llm, summarizer_prompt, num_tasks=4):
    graph = StateGraph(GraphState)
    graph.add_node("planner", RunnableLambda(planner_node))
    graph.add_node("combine", RunnableLambda(combine_node))

    # Add task handler nodes dynamically
    for i in range(num_tasks):
        handler = task_handler(i, run_logger, llm, summarizer_prompt)
        graph.add_node(f"task_{i}", RunnableLambda(handler))
        graph.add_edge("planner", f"task_{i}")
        graph.add_edge(f"task_{i}", "combine")

    graph.set_entry_point("planner")
    graph.add_edge("combine", END)
    return graph.compile()
