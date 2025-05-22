class Planner:
    def __init__(self, context):
        self.context = context

    def act(self):
        user_request = self.context.get("user_request")
        # convert user_request to lowercase
        user_request = user_request.lower()
        if "summarize" in user_request and "extract" in user_request:
            plan = (
                "1. Summarize the document.\n"
                "2. Extract involved parties.\n"
                "3. Extract expiration date."
            )
            self.context.update("task_plan", plan)
            print("[Planner] Task plan created.")
