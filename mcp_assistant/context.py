class SharedContext:
    def __init__(self):
        self.data = {
            "user_request": "",
            "task_plan": "",
            "task_result": "",
            "document_text": "",
        }

    def update(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key)

    def get_all(self):
        return self.data
