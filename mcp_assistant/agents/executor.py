import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Executor:
    def __init__(self, context):
        self.context = context

    def act(self):
        plan = self.context.get("task_plan")
        doc = self.context.get("document_text")
        if not plan or not doc:
            print("[Executor] No task or document to act on.")
            return

        prompt = (
            f"You are an intelligent contract assistant.\n\n"
            f"Document:\n{doc}\n\n"
            f"Instructions:\n{plan}\n"
        )

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a legal document assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )

        result = response.choices[0].message.content
        self.context.update("task_result", result)
        print("[Executor] Task completed using OpenAI.")
