class MCPMessage:
    def __init__(self, source, target, content, metadata=None):
        self.source = source
        self.target = target
        self.content = content
        # The metadata parameter allows attaching additional information to the message
        # as a dictionary of key-value pairs. If no metadata is provided, defaults to empty dict.
        self.metadata = metadata or {}
