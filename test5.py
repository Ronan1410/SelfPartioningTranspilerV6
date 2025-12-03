"""
Simplified Data Transfer Test - Uses Only Primitive Types
Tests cross-segment variable dependency with types the transpiler handles well
"""

# Segment 1: Rust - Data generation (produces int output)
def generate_sum(count):
    """
    Generate sum of sequence
    Expected: Rust (loops, math)
    OUTPUT: sum (int)
    """
    total = 0
    for i in range(count):
        total += i * 2
    return total


# Segment 2: Rust - Data processing (consumes from Segment 1, produces output)
def process_sum(total):
    """
    Process sum: square it
    Expected: Rust (math operations)
    INPUT: total (from segment 1)
    OUTPUT: squared (int)
    """
    squared = total * total
    return squared


# Segment 3: Rust - Transform (consumes from Segment 2, produces output)
def scale_result(squared):
    """
    Scale the result by 2
    Expected: Rust (arithmetic)
    INPUT: squared (from segment 2)
    OUTPUT: scaled (int)
    """
    scaled = squared * 2
    return scaled


# Segment 4: Java - Validation and display (consumes from Segment 3)
class ResultValidator:
    """
    Validate and display results using primitive types
    Expected: Java (OOP, display)
    INPUT: scaled (int from segment 3)
    """
    
    def __init__(self, scaled_value):
        self.scaled_value = scaled_value
        self.is_valid = True
        self.message = "Valid"
    
    def validate(self):
        """Validate the result"""
        if self.scaled_value > 0:
            self.is_valid = True
            self.message = "Result is positive and valid"
        else:
            self.is_valid = False
            self.message = "Result is invalid"
        return self.is_valid
    
    def display(self):
        """Display results"""
        if self.validate():
            print("=== Data Transfer Test Results ===")
            print("Scaled Value: " + str(self.scaled_value))
            print("Status: " + self.message)
            print("=== Test Completed Successfully ===")
        else:
            print("Validation Error: " + self.message)


# Main execution - demonstrates data flow between segments
if __name__ == "__main__":
    # Segment 1: Generate initial sum
    input_count = 5
    print("Step 1: Generating sum from " + str(input_count) + " numbers...")
    total = generate_sum(input_count)
    print("Generated total: " + str(total))
    
    # Segment 2: Square the sum
    print("\nStep 2: Processing sum (squaring)...")
    squared = process_sum(total)
    print("Squared: " + str(squared))
    
    # Segment 3: Scale the result
    print("\nStep 3: Scaling result...")
    scaled = scale_result(squared)
    print("Scaled: " + str(scaled))
    
    # Segment 4: Validate and display
    print("\nStep 4: Validating and displaying...")
    validator = ResultValidator(scaled)
    validator.display()
    
    # Show data flow chain
    print("\n=== Data Flow Chain ===")
    print("Segment 1 (generate_sum)")
    print("  OUTPUT: total = " + str(total))
    print("    |")
    print("    v")
    print("Segment 2 (process_sum)")
    print("  INPUT: total (from segment 1)")
    print("  OUTPUT: squared = " + str(squared))
    print("    |")
    print("    v")
    print("Segment 3 (scale_result)")
    print("  INPUT: squared (from segment 2)")
    print("  OUTPUT: scaled = " + str(scaled))
    print("    |")
    print("    v")
    print("Segment 4 (ResultValidator)")
    print("  INPUT: scaled (from segment 3)")
    print("  PROCESSING: Validation and display")
