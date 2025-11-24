"""
Edge Case Test 1: Empty functions, simple cases, and minimal code
Tests transpiler's handling of very simple/empty scenarios
"""

# 1. Empty function
def empty_function():
    pass

# 2. Single return
def single_return():
    return 42

# 3. Simple variable assignment
def simple_assign():
    x = 10
    return x

# 4. Single print statement
def single_print():
    print("Hello")

# 5. Simple if statement
def simple_if(x):
    if x > 0:
        print("Positive")

# 6. Simple for loop
def simple_for():
    for i in range(5):
        print(i)

# 7. Multiple statements
def multiple_statements():
    a = 1
    b = 2
    c = a + b
    return c
