"""
Edge Case Test 4: Classes and OOP features
Tests class definitions, methods, attributes
"""

# 1. Simple class
class SimpleClass:
    def __init__(self, value):
        self.value = value
    
    def get_value(self):
        return self.value

# 2. Class with multiple methods
class Calculator:
    def __init__(self):
        self.result = 0
    
    def add(self, x):
        self.result = self.result + x
        return self.result
    
    def multiply(self, x):
        self.result = self.result * x
        return self.result
    
    def reset(self):
        self.result = 0

# 3. Class with string operations
class MessageHandler:
    def __init__(self, prefix):
        self.prefix = prefix
    
    def format_message(self, msg):
        return self.prefix + ": " + msg
    
    def get_uppercase(self, text):
        return text.upper()

# 4. Class with conditional logic
class Validator:
    def __init__(self, max_value):
        self.max = max_value
    
    def validate(self, value):
        if value <= self.max:
            return True
        return False
    
    def check_range(self, value):
        if value >= 0 and value <= self.max:
            return "in range"
        elif value < 0:
            return "below zero"
        else:
            return "above max"

# 5. Class with instance variables
class Counter:
    def __init__(self, start):
        self.current = start
        self.max_count = 100
        self.name = "Counter"
    
    def increment(self):
        self.current = self.current + 1
        return self.current
    
    def is_max(self):
        return self.current >= self.max_count
