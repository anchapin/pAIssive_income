"""Mock MCP module."""

__version__ = "0.1.0"


class Client:
    def __init__(self, endpoint="", **kwargs) -> None:
        self.endpoint = endpoint
        self.kwargs = kwargs

    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        pass

    def send_message(self, message) -> str:
        return f"Mock MCP response to: {message}"


class Server:
    def __init__(self, name="mock-server", **kwargs) -> None:
        self.name = name
        self.kwargs = kwargs

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass
