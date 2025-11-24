"""
Edge Case Test 6: Mixed features - complex realistic scenarios
Tests combinations of features in realistic scenarios
"""
import asyncio

# 1. Function with mixed operations
def mixed_operations(n):
    result = 0
    for i in range(n):
        if i % 2 == 0:
            result = result + i
        else:
            result = result - i
    return result

# 2. Async with mixed control flow
async def async_mixed():
    items = 0
    limit = 5
    unused = 1000
    
    while items < limit:
        print(f"Processing item {items}")
        if items % 2 == 0:
            print("Even item")
        else:
            print("Odd item")
        items = items + 1
        await asyncio.sleep(0.1)
    
    return items

# 3. Class with complex logic
class DataProcessor:
    def __init__(self, capacity):
        self.items = 0
        self.capacity = capacity
        self.data = "processed"
    
    def add_item(self, item):
        if self.items < self.capacity:
            self.items = self.items + 1
            return True
        return False
    
    def is_full(self):
        return self.items >= self.capacity
    
    def get_status(self):
        percent = (self.items * 100) / self.capacity
        return f"Status: {percent}%"

# 4. Function with multiple conditions
def multi_condition(a, b, c, d):
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    return "all positive"
    if a < 0 and b < 0:
        return "a and b negative"
    if c == 0 or d == 0:
        return "c or d is zero"
    return "mixed"

# 5. Async with nested loops
async def async_nested_loops():
    for i in range(3):
        for j in range(3):
            print(f"{i},{j}")
            await asyncio.sleep(0.05)

# 6. Function with all arithmetic operators
def all_operators(x, y):
    add = x + y
    sub = x - y
    mul = x * y
    div = x / y if y != 0 else 0
    mod = x % y if y != 0 else 0
    power = x ** 2
    return add + sub + mul + mod + power

# 7. Loop with string building
def build_string():
    result = ""
    for i in range(5):
        result = result + str(i) + " "
    return result

# 8. Async with exception-like logic
async def async_safe_operation():
    value = 100
    attempts = 0
    max_attempts = 3
    
    while attempts < max_attempts:
        if value > 0:
            value = value - 20
            attempts = attempts + 1
            await asyncio.sleep(0.1)
        else:
            break
    
    return value
