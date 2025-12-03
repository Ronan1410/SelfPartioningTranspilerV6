"""
Comprehensive Test Case for SelfPartioningTranspiler V6

This test demonstrates:
- Math-heavy operations (Rust/C++)
- I/O and string operations (Go)
- Object-oriented code (Java)
- Data flow between segments
- Performance comparison potential
"""

def matrix_multiply(a, b, size):
    """
    Matrix multiplication - Pure math operations
    Expected: Rust or C++ (strong math support)
    Features: Nested loops, math ops, no I/O
    """
    result = [[0 for _ in range(size)] for _ in range(size)]
    
    for i in range(size):
        for j in range(size):
            for k in range(size):
                result[i][j] += a[i][k] * b[k][j]
    
    return result


def prime_checker(n):
    """
    Prime number checker with recursion
    Expected: C++ or Rust (recursion, math)
    Features: Math ops, conditional logic, no I/O
    """
    if n < 2:
        return False
    
    if n == 2:
        return True
    
    if n % 2 == 0:
        return False
    
    for i in range(3, int(n ** 0.5) + 1, 2):
        if n % i == 0:
            return False
    
    return True


def process_csv_data(data_lines):
    """
    CSV file processing with string operations
    Expected: Go (I/O, string operations)
    Features: Loop, string ops, I/O patterns
    """
    parsed_data = []
    
    for line in data_lines:
        fields = line.split(',')
        record = {
            'id': fields[0],
            'name': fields[1],
            'value': int(fields[2]),
            'status': fields[3].strip()
        }
        parsed_data.append(record)
        print(f"Processed: {record['id']} - {record['name']}")
    
    return parsed_data


class DataAnalyzer:
    """
    Object-oriented data analyzer
    Expected: Java (classes, OOP)
    Features: Classes, methods, state
    """
    
    def __init__(self, name):
        self.name = name
        self.data_points = []
        self.total = 0
        self.count = 0
    
    def add_data(self, value):
        """Add a data point and update statistics"""
        self.data_points.append(value)
        self.total += value
        self.count += 1
    
    def get_average(self):
        """Calculate average of all data points"""
        if self.count == 0:
            return 0.0
        return self.total / self.count
    
    def get_max(self):
        """Get maximum value"""
        if not self.data_points:
            return None
        return max(self.data_points)
    
    def get_summary(self):
        """Return summary statistics"""
        return {
            'name': self.name,
            'count': self.count,
            'total': self.total,
            'average': self.get_average(),
            'max': self.get_max()
        }


def fibonacci_sequence(n):
    """
    Generate fibonacci sequence
    Expected: Rust (recursion, math)
    Features: Recursion, list operations
    """
    def fib(num):
        if num <= 1:
            return num
        return fib(num - 1) + fib(num - 2)
    
    sequence = []
    for i in range(n):
        sequence.append(fib(i))
    
    return sequence


def string_processor(text):
    """
    Process text with multiple string operations
    Expected: Go (string ops)
    Features: String manipulation, I/O patterns
    """
    # Convert to uppercase
    upper_text = text.upper()
    
    # Count words
    words = text.split()
    word_count = len(words)
    
    # Find longest word
    longest = max(words, key=len) if words else ""
    
    # Print summary
    print(f"Original: {text}")
    print(f"Words: {word_count}")
    print(f"Longest word: {longest}")
    
    result = {
        'original': text,
        'uppercase': upper_text,
        'word_count': word_count,
        'longest_word': longest
    }
    
    return result


def merge_sorted_arrays(arr1, arr2):
    """
    Merge two sorted arrays
    Expected: C++ (arrays, algorithms)
    Features: Loops, comparisons, list operations
    """
    result = []
    i, j = 0, 0
    
    while i < len(arr1) and j < len(arr2):
        if arr1[i] <= arr2[j]:
            result.append(arr1[i])
            i += 1
        else:
            result.append(arr2[j])
            j += 1
    
    # Add remaining elements
    while i < len(arr1):
        result.append(arr1[i])
        i += 1
    
    while j < len(arr2):
        result.append(arr2[j])
        j += 1
    
    return result


class BankAccount:
    """
    Bank account with transactions
    Expected: Java (classes, state management)
    Features: Classes, methods, state
    """
    
    def __init__(self, account_id, initial_balance):
        self.account_id = account_id
        self.balance = initial_balance
        self.transactions = []
    
    def deposit(self, amount):
        """Deposit money to account"""
        if amount > 0:
            self.balance += amount
            self.transactions.append({
                'type': 'deposit',
                'amount': amount,
                'balance': self.balance
            })
            return True
        return False
    
    def withdraw(self, amount):
        """Withdraw money from account"""
        if amount > 0 and amount <= self.balance:
            self.balance -= amount
            self.transactions.append({
                'type': 'withdraw',
                'amount': amount,
                'balance': self.balance
            })
            return True
        return False
    
    def get_balance(self):
        """Get current balance"""
        return self.balance
    
    def print_statement(self):
        """Print account statement"""
        print(f"Account: {self.account_id}")
        print(f"Balance: ${self.balance}")
        print("Transactions:")
        for tx in self.transactions:
            print(f"  {tx['type']}: ${tx['amount']} (Balance: ${tx['balance']})")


def calculate_statistics(numbers):
    """
    Calculate multiple statistics
    Expected: Rust or C++ (math operations)
    Features: Math ops, loops, calculations
    """
    if not numbers:
        return None
    
    # Sum
    total = 0
    for n in numbers:
        total += n
    
    # Average
    average = total / len(numbers)
    
    # Variance
    variance_sum = 0
    for n in numbers:
        variance_sum += (n - average) ** 2
    variance = variance_sum / len(numbers)
    
    # Standard deviation
    std_dev = variance ** 0.5
    
    # Min and Max
    min_val = min(numbers)
    max_val = max(numbers)
    
    return {
        'sum': total,
        'average': average,
        'min': min_val,
        'max': max_val,
        'variance': variance,
        'std_dev': std_dev
    }


# Main execution
if __name__ == "__main__":
    print("=" * 70)
    print("SelfPartioningTranspiler V6 - Comprehensive Test Case")
    print("=" * 70)
    
    # Test 1: Matrix multiplication
    print("\n[Test 1] Matrix Multiplication (Math-heavy)")
    matrix_a = [[1, 2], [3, 4]]
    matrix_b = [[5, 6], [7, 8]]
    result = matrix_multiply(matrix_a, matrix_b, 2)
    print(f"Result: {result}")
    
    # Test 2: Prime checking
    print("\n[Test 2] Prime Checker (Recursion + Math)")
    test_numbers = [2, 17, 20, 29, 100]
    for num in test_numbers:
        is_prime = prime_checker(num)
        print(f"{num}: {'Prime' if is_prime else 'Not Prime'}")
    
    # Test 3: Fibonacci sequence
    print("\n[Test 3] Fibonacci Sequence (Recursion)")
    fib_seq = fibonacci_sequence(8)
    print(f"Fibonacci(8): {fib_seq}")
    
    # Test 4: Statistics calculation
    print("\n[Test 4] Statistics (Math Operations)")
    data = [10, 20, 30, 40, 50]
    stats = calculate_statistics(data)
    print(f"Stats for {data}:")
    print(f"  Average: {stats['average']:.2f}")
    print(f"  Std Dev: {stats['std_dev']:.2f}")
    print(f"  Min: {stats['min']}, Max: {stats['max']}")
    
    # Test 5: Array merging
    print("\n[Test 5] Merge Sorted Arrays (Algorithms)")
    arr1 = [1, 3, 5]
    arr2 = [2, 4, 6]
    merged = merge_sorted_arrays(arr1, arr2)
    print(f"Merged: {merged}")
    
    # Test 6: String processing
    print("\n[Test 6] String Processing (I/O + Strings)")
    text = "hello world testing"
    string_result = string_processor(text)
    print(f"Processed: {len(string_result)} fields extracted")
    
    # Test 7: CSV data processing
    print("\n[Test 7] CSV Processing (I/O + Parsing)")
    csv_data = [
        "1,Alice,100,Active",
        "2,Bob,200,Inactive",
        "3,Charlie,150,Active"
    ]
    parsed = process_csv_data(csv_data)
    print(f"Parsed {len(parsed)} records")
    
    # Test 8: Data analyzer class
    print("\n[Test 8] Data Analyzer (OOP)")
    analyzer = DataAnalyzer("TestData")
    for value in [10, 20, 30, 40, 50]:
        analyzer.add_data(value)
    summary = analyzer.get_summary()
    print(f"Summary: {summary}")
    
    # Test 9: Bank account
    print("\n[Test 9] Bank Account (OOP + State)")
    account = BankAccount("ACC001", 1000)
    account.deposit(500)
    account.withdraw(200)
    account.withdraw(150)
    print(f"Final balance: ${account.get_balance()}")
    
    print("\n" + "=" * 70)
    print("✓ All tests completed successfully!")
    print("=" * 70)
