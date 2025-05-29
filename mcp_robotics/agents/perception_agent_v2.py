import os
import base64
import time
from io import BytesIO

import cv2
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
from ultralytics import YOLO

from context.agent import Agent
from context.mcp_message import MCPMessage

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Load the model
model = YOLO("yolo11n.pt")

class PerceptionAgent(Agent):
    def __init__(self, name="Perception"):
        super().__init__(name)

    def process(self, message: MCPMessage):
        # Simulate processing visual input
        image_data = message.content  # image data in bytes
        try:
            if isinstance(image_data, str):
                image_data = image_data.encode('utf-8')
            else:
                # convert image bytes to numpy array
                image_data = np.frombuffer(image_data, dtype=np.uint8)
                image_data = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

        except Exception as e:
            raise ValueError("Unsupported image data type: " + str(type(image_data))+" Error: ", e)
        
        # Start perception pipeline
        # run object detection
        image_with_boxes = self.object_detection(image_data)
        # convert numpy array image to base64
        image_with_boxes_base64 = self.convert_image_to_base64(image_with_boxes)
        # Use GPT for labeling assistance
        description = self.describe_image(image_with_boxes_base64)
        # send description to planning agent
        return MCPMessage(source=self.name, target="Planning", content=description)

    # helper functions
    # convert image to base64
    def convert_image_to_base64(self, image_data):
        # If your image is BGR (from OpenCV), convert to RGB first
        image_rgb = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
        # Convert to PIL Image
        pil_image = Image.fromarray(image_rgb)
        # Save image to a bytes buffer
        buffer = BytesIO()
        pil_image.save(buffer, format="PNG")  # You can use "JPEG" or "WEBP" as well
        #buffer.seek(0)
        # Convert buffer to base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        # return base64 image
        return image_base64

    # describe image
    def describe_image(self, image_data):
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-4-vision-preview"
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": "Describe shortly the objects in the image, describe just the nearest objects and try to estimate the distance to the objects within label boxes and rank how dangerous a collision would be."},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}"
                    }}
                ]}
            ],
            max_tokens=200,
            temperature=0
        )
        return response.choices[0].message.content
    
    def object_detection(self, image_data: np.ndarray, device: str = 'cpu'):
        # preprocess image
        # image_data = cv2.resize(image_data, (320, 320))
        # image_data = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
        # Inference
        results = model.predict(source=image_data, device=device, imgsz=320, conf=0.4, verbose=False)
        # Results[0] holds detections for the first (and here only) image

        # Draw boxes on image
        img = image_data
        for r in results:
            boxes = r.boxes
            for box in boxes:
                coords = box.xyxy[0].cpu().numpy().astype(int)
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                label = f"{model.names[cls]}:{conf:.2f}"
                cv2.rectangle(img, tuple(coords[:2]), tuple(coords[2:]), (255,0,0), 2)
                cv2.putText(img, label, (coords[0], coords[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)

        # Save image
        img_file = f"detection_{time.time()}.png"
        cv2.imwrite(img_file, img)
        # return image with boxes
        return img
    