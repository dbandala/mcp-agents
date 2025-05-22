from context.agent import Agent
from context.mcp_message import MCPMessage

class ControlAgent(Agent):
    def __init__(self, name="Control"):
        super().__init__(name)

    def process(self, message: MCPMessage):
        plan = message.content
        # Here you’d generate motor commands (mocked)
        # or we could set the gains for the motors or PID controllers
        # or we could set the target position for the robot
        # or we could set the target velocity for the robot
        # or we could set the target acceleration for the robot
        # or we could set the target torque for the robot

        print(f"[Control] Executing plan: {plan}")
        return MCPMessage(source=self.name, target=None, content="Plan executed")
