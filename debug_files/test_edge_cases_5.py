"""
Edge Case Test 5: Mathematical operations, operators, edge values
Tests mathematical operations, comparisons, various operator types
"""

# 1. Arithmetic operations
def arithmetic_ops():
    a = 10
    b = 3
    add = a + b
    sub = a - b
    mul = a * b
    div = a / b
    mod = a % b
    return add + sub + mul + mod

# 2. Power operations
def power_operations():
    x = 2
    y = x ** 3
    z = y ** 2
    return z

# 3. Comparisons
def comparison_ops(x, y):
    if x < y:
        return "less"
    if x == y:
        return "equal"
    if x > y:
        return "greater"
    if x <= y:
        return "less or equal"
    if x >= y:
        return "greater or equal"
    if x != y:
        return "not equal"
    return "unknown"

# 4. Logical operations
def logical_ops(a, b, c):
    if a and b:
        return "both true"
    if a or c:
        return "at least one true"
    if not a:
        return "a is false"
    return "complex"

# 5. Modulo operations
def modulo_check(n):
    if n % 2 == 0:
        return "even"
    else:
        return "odd"

# 6. Increment/Decrement style
def increment_operations():
    x = 0
    x = x + 1
    x = x + 1
    x = x + 1
    return x

# 7. Augmented assignments
def augmented_assign():
    x = 10
    x = x + 5
    x = x - 3
    x = x * 2
    return x

# 8. Negative numbers
def negative_numbers():
    a = -10
    b = -5
    c = a + b
    d = a * b
    e = a - b
    return c + d + e

# 9. Division by expressions
def division_expr(x, y):
    result = (x + y) / (x - y)
    return result
