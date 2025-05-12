from graph import graph

query = "Analyze HIMS stock after earnings"

inputs = {"input": query}
output = graph.invoke(inputs)

print("\n" + "=" * 30 + "\n")
print(output["final_output"])