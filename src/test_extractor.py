import ast
import re

class TestExtractor:
    """
    Extracts test values from the if __name__ == "__main__" block
    and maps them to function calls.
    """
    
    @staticmethod
    def extract_test_calls(code):
        """
        Extract test calls and their arguments from Python code.
        Returns a dict mapping function names to test parameters.
        """
        tree = ast.parse(code)
        test_calls = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Look for main block
                test = node.test
                if (isinstance(test, ast.Compare) and 
                    isinstance(test.left, ast.Name) and 
                    test.left.id == '__name__'):
                    
                    # Extract all calls in main block
                    for stmt in node.body:
                        TestExtractor._extract_from_stmt(stmt, test_calls)
        
        return test_calls
    
    @staticmethod
    def _extract_from_stmt(stmt, test_calls, depth=0):
        """Recursively extract test calls from statements."""
        if isinstance(stmt, ast.Assign):
            # Look at assignments that might be test data
            # e.g., result = matrix_multiply(matrix_a, matrix_b, 2)
            if isinstance(stmt.value, ast.Call):
                TestExtractor._extract_call(stmt.value, test_calls)
        
        elif isinstance(stmt, ast.Expr):
            # Expression statements (like print() or function calls)
            if isinstance(stmt.value, ast.Call):
                TestExtractor._extract_call(stmt.value, test_calls)
        
        elif isinstance(stmt, ast.For):
            # For loops with function calls
            for substmt in stmt.body:
                TestExtractor._extract_from_stmt(substmt, test_calls, depth + 1)
        
        elif isinstance(stmt, ast.If):
            # If statements
            for substmt in stmt.body:
                TestExtractor._extract_from_stmt(substmt, test_calls, depth + 1)
            for substmt in stmt.orelse:
                TestExtractor._extract_from_stmt(substmt, test_calls, depth + 1)
    
    @staticmethod
    def _extract_call(call_node, test_calls):
        """Extract a single function call with its arguments."""
        if isinstance(call_node.func, ast.Name):
            func_name = call_node.func.id
            args = TestExtractor._extract_args(call_node.args)
            
            if func_name not in test_calls:
                test_calls[func_name] = []
            test_calls[func_name].append(args)
    
    @staticmethod
    def _extract_args(args):
        """Convert AST argument nodes to Python values."""
        result = []
        for arg in args:
            result.append(TestExtractor._ast_to_value(arg))
        return result
    
    @staticmethod
    def _ast_to_value(node):
        """Convert an AST node to a Python value."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            return node.id  # Return as variable name
        elif isinstance(node, ast.List):
            return [TestExtractor._ast_to_value(e) for e in node.elts]
        elif isinstance(node, ast.Tuple):
            return tuple(TestExtractor._ast_to_value(e) for e in node.elts)
        elif isinstance(node, ast.Dict):
            return {TestExtractor._ast_to_value(k): TestExtractor._ast_to_value(v) 
                    for k, v in zip(node.keys, node.values)}
        elif isinstance(node, ast.Call):
            # For constructor/function calls in args
            if isinstance(node.func, ast.Name):
                return f"{node.func.id}({', '.join(str(TestExtractor._ast_to_value(a)) for a in node.args)})"
            return str(node)
        else:
            return str(node)
    
    @staticmethod
    def get_test_value_for_function(func_name, test_calls_map):
        """
        Get the most appropriate test value for a function.
        For functions called multiple times, return the first call's args.
        """
        if func_name in test_calls_map:
            calls = test_calls_map[func_name]
            if calls:
                return calls[0]  # Return first call's arguments
        return None
    
    @staticmethod
    def build_test_data_map(code):
        """
        Build a comprehensive mapping of test data from Python code.
        """
        test_calls = TestExtractor.extract_test_calls(code)
        
        # Also extract variable assignments from main block
        tree = ast.parse(code)
        variables = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Look for main block
                test = node.test
                if (isinstance(test, ast.Compare) and 
                    isinstance(test.left, ast.Name) and 
                    test.left.id == '__name__'):
                    
                    # Extract variable assignments
                    for stmt in node.body:
                        if isinstance(stmt, ast.Assign):
                            for target in stmt.targets:
                                if isinstance(target, ast.Name):
                                    var_name = target.id
                                    var_value = TestExtractor._ast_to_value(stmt.value)
                                    variables[var_name] = var_value
        
        return {
            'function_calls': test_calls,
            'variables': variables
        }
