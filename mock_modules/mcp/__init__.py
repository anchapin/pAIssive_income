"""Mock MCP module."""
__version__ = "0.1.0"

class Client:
    def __init__(self, endpoint="", **kwargs):
        self.endpoint = endpoint
        self.kwargs = kwargs
    
    def connect(self):
        pass
    
    def disconnect(self):
        pass
    
    def send_message(self, message):
        return f"Mock MCP response to: {message}"

class Server:
    def __init__(self, name="mock-server", **kwargs):
        self.name = name
        self.kwargs = kwargs
    
    def start(self):
        pass
    
    def stop(self):
        pass
