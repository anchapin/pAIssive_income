"""
Minimal stub for the hypothesis package.
"""

from functools import wraps

def given(*args, **kwargs):
    def decorator(func):
        return func
    return decorator

class strategies:
    pass

def assume(condition):
    pass

class settings:
    def __init__(self, **kwargs):
        pass
    def __call__(self, func):
        return func

def example(*args, **kwargs):
    def decorator(func):
        return func
    return decorator
