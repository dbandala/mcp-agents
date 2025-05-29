import os
from dotenv import load_dotenv
from openai import OpenAI

from context.agent import Agent
from context.mcp_message import MCPMessage

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

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

        controls_instructions = '''
        The commands should be in the format of a ROS2 action or service call, write just the list of commands, not the ROS2 action or service call:
        geometry_msgs/Twist {
            Vector3 linear  { x: 0.5, y: 0.0, z: 0.0 }
            Vector3 angular { x: 0.0, y: 0.0, z: 0.1 }
        }
        '''

        # Use GPT to generate a strategic plan
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a robotics control agent. You are given a plan description of what to do next and you have to translate it into a list of ROS2 commands."},
                {"role": "user", "content": f"""Given this plan description: {plan}, translate into a list of ROS2 commands.
                    {controls_instructions}
                 """}
            ],
            temperature=0,
            max_tokens=400
        )

        print(f"[Control] Executing plan: {response.choices[0].message.content}")
        return MCPMessage(source=self.name, target=None, content=response.choices[0].message.content)
