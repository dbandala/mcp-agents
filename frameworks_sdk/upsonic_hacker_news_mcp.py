import os
from dotenv import load_dotenv
from upsonic import Task, Agent, Direct
from upsonic.client.tools import Search  # Adding Search as a fallback tool

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file")

# Set your OpenAI API key for the session
os.environ["OPENAI_API_KEY"] = openai_api_key

# Define the HackerNews MCP tool
# Using the correct MCP setup for HackerNews based on Upsonic documentation
class HackerNewsMCP:
    command = "uvx"
    args = ["mcp-hn"]
    # No environment variables are needed for this MCP

# Create a task to analyze the latest HackerNews stories
# Adding Search as a fallback in case HackerNews MCP fails
task = Task(
    "Analyze the top 5 HackerNews stories for today. Provide a brief summary of each story, "
    "identify any common themes or trends, and highlight which stories might be most relevant "
    "for someone interested in AI and software development.",
    tools=[HackerNewsMCP, Search]  # Include both HackerNews MCP and Search tools
)

# Create an agent specialized in tech news analysis
agent = Agent(
    "Tech News Analyst",
    company_url="https://news.ycombinator.com/",
    company_objective="To provide insightful analysis of tech industry news and trends"
)

# Execute the task with the agent and print the results
print("Analyzing HackerNews stories...")
agent.print_do(task)

# Alternatively, you can use a Direct LLM call if the task is straightforward
# print("Direct analysis of HackerNews stories...")
# Direct.print_do(task)

# If you want to access the response programmatically:
# agent.do(task)
# result = task.response
# print(result)