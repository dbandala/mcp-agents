import os
import base64

import cv2
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

from context.agent import Agent
from context.mcp_message import MCPMessage

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

class PerceptionAgent(Agent):
    def __init__(self, name="Perception"):
        super().__init__(name)

    def process(self, message: MCPMessage):
        # Simulate processing visual input
        image_data = message.content  # filename
        try:
            if isinstance(image_data, str):
                image_data = image_data.encode('utf-8')
            else:
                image_data = self.convert_image_to_base64(image_data)
        except Exception as e:
            raise ValueError("Unsupported image data type: " + str(type(image_data))+" Error: ", e)
        

        print("image_data: ", image_data, "\n\n")
        
        # Use GPT for labeling assistance
        description = self.describe_image(image_data)
        # send description to planning agent
        return MCPMessage(source=self.name, target="Planning", content=description)

    # helper functions
    # convert image to base64
    def convert_image_to_base64(self, image_data):
        return base64.b64encode(image_data).decode('utf-8')

    # describe image
    def describe_image(self, image_data):
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-4-vision-preview"
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": "What’s in this image?"},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}"
                    }}
                ]}
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content