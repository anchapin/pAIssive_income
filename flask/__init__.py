"""
Minimal stub for the flask package.
"""


import json

class Flask:
    def __init__(self, import_name):
        self.import_name = import_name

    def run(self, *args, **kwargs):
        pass

def has_request_context():
    """Minimal stub for has_request_context."""
    return True # Assuming a request context for testing purposes

# Alias json to the standard json library for simplicity in the stub
# from flask import json -> import json as flask_json
# flask_json = json
