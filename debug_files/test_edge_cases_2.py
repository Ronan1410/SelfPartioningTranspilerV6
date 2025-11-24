"""
Edge Case Test 2: Complex control flow, nested structures
Tests transpiler's handling of nested loops, if/else chains, etc.
"""

# 1. Nested loops
def nested_loops():
    for i in range(3):
        for j in range(3):
            print(i + j)

# 2. If-elif-else
def if_elif_else(x):
    if x < 0:
        return "negative"
    elif x == 0:
        return "zero"
    else:
        return "positive"

# 3. Nested if statements
def nested_if(x, y):
    if x > 0:
        if y > 0:
            return "both positive"
        else:
            return "x positive"

# 4. Loop with if inside
def loop_with_if():
    for i in range(10):
        if i % 2 == 0:
            print(i)

# 5. While loop (important for Go transpiler)
def while_loop():
    x = 0
    while x < 5:
        print(x)
        x = x + 1

# 6. Complex boolean conditions
def complex_conditions(a, b, c):
    if a > 0 and b > 0:
        if c != 0:
            return True
    return False
