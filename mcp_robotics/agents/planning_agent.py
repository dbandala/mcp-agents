import os
from dotenv import load_dotenv

from context.agent import Agent
from context.mcp_message import MCPMessage
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

class PlanningAgent(Agent):
    def __init__(self, name="Planning"):
        super().__init__(name)

    def process(self, message: MCPMessage):
        perception_description = message.content
        # Use GPT to generate a strategic plan
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a robotics planning agent. You are given a description of the environment and you need to generate a list of actions to take in order to avoid obstacles."},
                {"role": "user", "content": f"Given this perception description: {perception_description}, what should I do next? Make a list of actions to take."}
            ],
            temperature=0,
            max_tokens=400
        )
        return MCPMessage(source=self.name, target="Control", content=response.choices[0].message.content)
