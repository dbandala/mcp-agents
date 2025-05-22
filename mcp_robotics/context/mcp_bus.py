from context.agent import Agent
from context.mcp_message import MCPMessage

class MCPBus:
    def __init__(self):
        self.agents = {}

    def register_agent(self, agent: Agent):
        self.agents[agent.name] = agent

    def send(self, message: MCPMessage):
        target = self.agents.get(message.target)
        if target:
            return target.process(message)
        else:
            raise Exception(f"Target agent '{message.target}' not found.")
