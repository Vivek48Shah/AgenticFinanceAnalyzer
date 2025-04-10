from dotenv import load_dotenv
load_dotenv()
from graph import build_graph
from logger import RunLogger
from state import summarize_prompt
from langchain_openai import ChatOpenAI

def main():
    run_logger = RunLogger()
    llm = ChatOpenAI(model="gpt-4o-mini",temperature=0.2)

    user_query = input("Enter your financial research query: ")
    graph_executor = build_graph(run_logger, llm, summarize_prompt)

    result = graph_executor.invoke({"input": user_query})

    print("\n===== Final Report =====\n")
    

    run_logger.log_report(result["report"])
    run_logger.finalize(query=user_query, total_tasks=len(result.get("summaries", [])))

    print(f"\nLogs and report saved at: {run_logger.get_run_path()}")


if __name__ == "__main__":
    main()
