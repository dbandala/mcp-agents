class Context:
    def __init__(self):
        self.data = {"task": None, "state": {}, "memory": {}}

    def update(self, updates: dict):
        self.data.update(updates)

    def get(self):
        return self.data

class Model:
    def __init__(self, name, context: Context):
        self.name = name
        self.context = context

    def act(self):
        raise NotImplementedError

class Planner(Model):
    def act(self):
        context = self.context.get()
        if not context["task"]:
            self.context.update({"task": "Plan step A"})
            print(f"{self.name} set task to Plan step A")

class Executor(Model):
    def act(self):
        task = self.context.get().get("task")
        if task == "Plan step A":
            print(f"{self.name} executes: {task}")
            self.context.update({"task": None})

context = Context()
models = [Planner("Planner", context), Executor("Executor", context)]

for model in models:
    model.act()
    print("Model context: ", model.context.get(), "\n")
