"""
Edge Case Test 3: Async operations, I/O, strings
Tests async functions, await statements, string operations
"""
import asyncio

# 1. Async function with await
async def async_simple():
    print("Starting")
    await asyncio.sleep(0.1)
    print("Done")

# 2. Async with loop
async def async_with_loop():
    for i in range(3):
        print(f"Iteration {i}")
        await asyncio.sleep(0.05)

# 3. Async with while loop (Go transpiler test)
async def async_while_loop():
    count = 0
    unused_var = 999
    while count < 3:
        print(f"Count: {count}")
        count = count + 1
        await asyncio.sleep(0.1)

# 4. String operations
def string_operations():
    s1 = "Hello"
    s2 = "World"
    result = s1 + " " + s2
    print(result)
    return result

# 5. String in f-string
def f_string_test(name, age):
    return f"Name: {name}, Age: {age}"

# 6. Multiple string concatenations
def multi_concat():
    msg = "Line 1 " + "Line 2 " + "Line 3"
    print(msg)
    return msg

# 7. Async function with conditional
async def async_conditional(x):
    if x > 0:
        print("Positive value")
        await asyncio.sleep(0.1)
    else:
        print("Non-positive value")
    return x
