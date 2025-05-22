from context import SharedContext
from agents.planner import Planner
from agents.executor import Executor

# Simulated user request and document
user_input = "Summarize this contract and extract the parties and expiration date."
contract_text = """
This agreement is made between Acme Corp and Beta Ltd. It is effective from Jan 1, 2024,
and will expire on Dec 31, 2025. The contract outlines responsibilities for supply chain logistics.
"""

# Initialize context and agents
ctx = SharedContext()
ctx.update("user_request", user_input)
ctx.update("document_text", contract_text)

planner = Planner(ctx)
executor = Executor(ctx)

# Run MCP steps
planner.act()
executor.act()
#print("Executor context: ", ctx.get_all(), "\n")

# Display results
print("\n=== Final Output ===")
print(ctx.get("task_result"))
