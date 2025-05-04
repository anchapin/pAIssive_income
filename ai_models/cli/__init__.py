"""
"""
Command-line interface for AI models.
Command-line interface for AI models.


This package provides a command-line interface for managing AI models,
This package provides a command-line interface for managing AI models,
including downloading, serving, and optimizing models.
including downloading, serving, and optimizing models.
"""
"""




from .cli import main
from .cli import main


(
(
BenchmarkCommand,
BenchmarkCommand,
DeployCommand,
DeployCommand,
DownloadCommand,
DownloadCommand,
InfoCommand,
InfoCommand,
ListCommand,
ListCommand,
OptimizeCommand,
OptimizeCommand,
ServeGRPCCommand,
ServeGRPCCommand,
ServeRESTCommand,
ServeRESTCommand,
ValidateCommand,
ValidateCommand,
)
)


__all__ = [
__all__ = [
"main",
"main",
"DownloadCommand",
"DownloadCommand",
"ListCommand",
"ListCommand",
"InfoCommand",
"InfoCommand",
"ServeRESTCommand",
"ServeRESTCommand",
"ServeGRPCCommand",
"ServeGRPCCommand",
"OptimizeCommand",
"OptimizeCommand",
"BenchmarkCommand",
"BenchmarkCommand",
"DeployCommand",
"DeployCommand",
"ValidateCommand",
"ValidateCommand",
]
]