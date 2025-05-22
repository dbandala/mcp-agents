from context.mcp_message import MCPMessage

class Agent:
    def __init__(self, name):
        self.name = name

    def process(self, message: MCPMessage):
        raise NotImplementedError
