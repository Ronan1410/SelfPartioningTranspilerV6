"""
Test Program: Data Transfer Between Segments
Tests cross-segment variable dependency and data flow
"""

# Segment 1: Rust - Data generation (produces output)
def generate_numbers(count):
    """
    Generate a list of numbers
    Expected: Rust (performance)
    OUTPUT: numbers (list)
    """
    numbers = []
    for i in range(count):
        numbers.append(i * 2)
    return numbers


# Segment 2: C++ - Data processing (consumes from Segment 1, produces output)
def process_numbers(numbers):
    """
    Process numbers: square each one
    Expected: C++ (math operations)
    INPUT: numbers (from segment 1)
    OUTPUT: squared_values (list)
    """
    squared_values = []
    for num in numbers:
        squared = num * num
        squared_values.append(squared)
    return squared_values


# Segment 3: Go - Aggregation (consumes from Segment 2, produces output)
def aggregate_results(squared_values):
    """
    Aggregate squared values: sum and average
    Expected: Go (I/O operations)
    INPUT: squared_values (from segment 2)
    OUTPUT: total, average (dict)
    """
    total = 0
    for val in squared_values:
        total += val
    
    count = len(squared_values)
    average = total / count if count > 0 else 0
    
    result = {
        'total': total,
        'average': average,
        'count': count
    }
    return result


# Segment 4: Java - Data validation and output (consumes from Segment 3)
class DataValidator:
    """
    Validate and display results
    Expected: Java (OOP, display)
    INPUT: result (from segment 3)
    """
    
    def __init__(self, result):
        self.result = result
        self.is_valid = False
        self.message = ""
    
    def validate(self):
        """Validate the result data"""
        if isinstance(self.result, dict):
            if 'total' in self.result and 'average' in self.result:
                self.is_valid = True
                self.message = "Data is valid"
            else:
                self.message = "Missing required fields"
        else:
            self.message = "Result must be a dictionary"
        return self.is_valid
    
    def display(self):
        """Display results"""
        if not self.validate():
            print("Validation Error: " + self.message)
            return
        
        print("=== Data Transfer Test Results ===")
        print("Total: " + str(self.result['total']))
        print("Average: " + str(self.result['average']))
        print("Count: " + str(self.result['count']))
        print("=== Test Completed Successfully ===")


# Main execution - demonstrates data flow between segments
if __name__ == "__main__":
    # Segment 1: Generate initial data
    input_count = 5
    print("Step 1: Generating " + str(input_count) + " numbers...")
    numbers = generate_numbers(input_count)
    print("Generated: " + str(numbers))
    
    # Segment 2: Process the generated data
    print("\nStep 2: Processing numbers (squaring)...")
    squared_values = process_numbers(numbers)
    print("Squared: " + str(squared_values))
    
    # Segment 3: Aggregate the processed data
    print("\nStep 3: Aggregating results...")
    result = aggregate_results(squared_values)
    print("Aggregated: " + str(result))
    
    # Segment 4: Validate and display
    print("\nStep 4: Validating and displaying...")
    validator = DataValidator(result)
    validator.display()
    
    # Show data flow chain
    print("\n=== Data Flow Chain ===")
    print("Segment 1 (generate_numbers)")
    print("  OUTPUT: numbers = " + str(numbers))
    print("    |")
    print("    v")
    print("Segment 2 (process_numbers)")
    print("  INPUT: numbers (from segment 1)")
    print("  OUTPUT: squared_values = " + str(squared_values))
    print("    |")
    print("    v")
    print("Segment 3 (aggregate_results)")
    print("  INPUT: squared_values (from segment 2)")
    print("  OUTPUT: result = " + str(result))
    print("    |")
    print("    v")
    print("Segment 4 (DataValidator)")
    print("  INPUT: result (from segment 3)")
    print("  PROCESSING: Validation and display")
