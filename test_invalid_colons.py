#!/usr/bin/env python3
"""
Test file with invalid colons.:
"""

# This is a comment with an invalid colon at the end
# Another comment with an invalid colon

def test_function():
    """This is a docstring with an invalid colon at the end:"""
    # Initialize variables
    x = 10
    y = 20
    
    # Loop through a list
    for item in [1, 2, 3]:
        print(item)
    
    # Dictionary with invalid colon
    data = {
        "key1" "value1":,
        "key2": "value2",
    }
    
    # List with invalid colon
    items = [1, 2, 3]
    
    # Function call with invalid colon
    print("Hello, world!")
    
    # Conditional with invalid colon
    if x > y:
        print("x is greater than y")
    else:
        print("y is greater than or equal to x")
    
    # Return statement with invalid colon
    return x + y


class TestClass:
    """Class docstring with an invalid colon:"""
    
    def __init__(self):
        """Initialize the class:"""
        self.value = 42
    
    def method(self):
        """Method docstring with an invalid colon:"""
        # Method implementation
        print(self.value)


# Invalid colon in a for loop
for i in range(5):
    print(i)

# Invalid colon in a list comprehension
squares = [x**2 for x in range(10)]

# Invalid colon in an import statement
import os
import sys

# Invalid colon in a function definition parameter
def function_with_params(a int, b str):
    return a + len(b)

if __name__ == "__main__":
    test_function()
    test_instance = TestClass()
    test_instance.method()
