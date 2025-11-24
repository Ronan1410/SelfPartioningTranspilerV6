import asyncio

# 1. Target: Rust
# High Math intensity and Loops favored by Rust in our cost model.
def heavy_computation_matrix():
    result = 0
    # Multiple nested loops
    for i in range(100):
        for j in range(100):
            # Heavy math operations
            val = (i * j) + (i - j) / (i + 1)
            val = val ** 2
            val = val % 10
            result += val
    return result

# 2. Target: C++ 
# Recursion and Math are favored by C++.
def recursive_factorial_algorithm(n):
    # Recursion
    if n <= 1:
        return 1
    else:
        # Math ops mixed with recursion
        return n * recursive_factorial_algorithm(n - 1)

# 3. Target: Go
# IO, Async, and Strings are favored by Go.
async def concurrent_log_processor():
    # Async definition triggers async_ops
    # Lots of IO (print)
    print("Starting processor")
    print("Reading stream...")
    
    data = "some string data" 
    processed = data + " processed" # string ops
    
    print(f"Log entry: {processed}")
    print("Flushing buffer...")
    print("Closing connection...")
    await asyncio.sleep(1)

# 4. Target: Java
# Classes (OOP) and Strings are favored by Java.
class EnterpriseCustomerManager:
    def __init__(self, name):
        self.name = name
        self.status = "Active" # string op

    def get_customer_details(self):
        # String manipulation
        return "Customer: " + self.name + " [" + self.status + "]"

    def update_status(self, new_status):
        self.status = new_status
        return self.status.upper() # string op

    def validate(self):
        return isinstance(self.name, str)
