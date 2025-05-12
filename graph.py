from langgraph.graph import StateGraph, END

from planner import planner_node
from combine import combine_node
from langchain_core.runnables import RunnableLambda


from agents.router import route_task
from state import State
from combine import combine_outputs

NUM_TASKS = 4


planner = RunnableLambda(planner_node)

# Each task is a modular Runnable
def make_task_node(i):
    return RunnableLambda(lambda state: {
        "summaries": state.get("summaries", []) + [route_task(state["tasks"][i], i)]
    })

# Final combine node
combine = RunnableLambda(lambda state: {
    "final_output": combine_outputs(state["summaries"])
})

# Build the LangGraph
graph_builder = StateGraph(State)

# Add all nodes
graph_builder.add_node("planner", planner)

for i in range(NUM_TASKS):
    graph_builder.add_node(f"task_{i}", make_task_node(i))

graph_builder.add_node("combine", combine)

# Define edges
graph_builder.set_entry_point("planner")

for i in range(NUM_TASKS):
    prev = "planner" if i == 0 else f"task_{i-1}"
    graph_builder.add_edge(prev, f"task_{i}")

graph_builder.add_edge(f"task_{NUM_TASKS - 1}", "combine")
graph_builder.add_edge("combine", END)

# Compile graph
graph = graph_builder.compile()
