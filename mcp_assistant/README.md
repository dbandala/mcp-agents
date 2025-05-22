let’s walk through a real-life example of a Model Context Protocol (MCP) using the OpenAI API with two cooperating agents (models):

A Planner agent: determines what task to do based on user goals.

An Executor agent: uses the OpenAI API to generate specific output for that task.

They share a structured context object that evolves as the conversation or workflow progresses.

We’ll simulate an intelligent document assistant where the user asks:

“Summarize this contract and extract the parties and expiration date.”