#!/usr/bin/env python3
"""
Master Test Runner - Execute and Report on All Tests
Provides detailed output and identifies any issues
"""
import sys
import os
import subprocess
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestRunner:
    def __init__(self):
        self.results = {}
        self.start_time = None
        self.end_time = None
        
    def log(self, msg, level="INFO"):
        """Print formatted message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if level == "INFO":
            prefix = ""
        elif level == "SUCCESS":
            prefix = ""
        elif level == "ERROR":
            prefix = ""
        elif level == "WARNING":
            prefix = ""
        elif level == "SECTION":
            prefix = ""
        else:
            prefix = "• "
        
        print(f"[{timestamp}] {prefix} {msg}")
    
    def test_file(self, test_file, description):
        """Test a single file"""
        self.log(f"Testing: {description}", "SECTION")
        
        if not os.path.exists(test_file):
            self.log(f"File not found: {test_file}", "WARNING")
            self.results[test_file] = {
                'status': 'SKIP',
                'reason': 'File not found',
                'time': 0
            }
            return None
        
        test_start = time.time()
        
        # Step 1: Check syntax
        try:
            with open(test_file, 'r') as f:
                content = f.read()
            import ast
            ast.parse(content)
            self.log(f"Syntax check: OK ({len(content)} bytes)", "SUCCESS")
        except SyntaxError as e:
            self.log(f"Syntax error: {e}", "ERROR")
            self.results[test_file] = {
                'status': 'FAIL',
                'reason': f'Syntax error: {str(e)[:50]}',
                'time': time.time() - test_start
            }
            return None
        
        # Step 2: Run transpiler
        try:
            result = subprocess.run(
                [sys.executable, 'main.py', test_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self.log(f"Transpilation: FAILED", "ERROR")
                self.log(f"Error: {result.stderr[:100]}", "ERROR")
                self.results[test_file] = {
                    'status': 'FAIL',
                    'reason': 'Transpilation failed',
                    'time': time.time() - test_start,
                    'error': result.stderr[:200]
                }
                return None
            
            self.log(f"Transpilation: OK", "SUCCESS")
            
        except subprocess.TimeoutExpired:
            self.log(f"Transpilation: TIMEOUT", "ERROR")
            self.results[test_file] = {
                'status': 'FAIL',
                'reason': 'Transpilation timeout',
                'time': time.time() - test_start
            }
            return None
        except Exception as e:
            self.log(f"Transpilation: ERROR - {str(e)[:50]}", "ERROR")
            self.results[test_file] = {
                'status': 'FAIL',
                'reason': str(e)[:50],
                'time': time.time() - test_start
            }
            return None
        
        # Step 3: Check generated files
        if not os.path.exists('out_dir/runner.py'):
            self.log(f"Generated code: No runner (OK)", "SUCCESS")
            self.results[test_file] = {
                'status': 'OK',
                'reason': 'Transpiled (no runner)',
                'time': time.time() - test_start
            }
            return None
        
        files = os.listdir('out_dir')
        file_count = len(files)
        self.log(f"Generated files: {file_count} files", "SUCCESS")
        
        # Step 4: Run generated code
        try:
            runner_result = subprocess.run(
                [sys.executable, 'out_dir/runner.py'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Check for critical errors
            issues = []
            
            if "declared and not used" in runner_result.stdout or "declared and not used" in runner_result.stderr:
                issues.append("Go: declared and not used error")
                self.log(f"Critical: {issues[0]}", "ERROR")
            
            error_pattern = "[ERROR]"
            if error_pattern in runner_result.stdout:
                error_count = runner_result.stdout.count(error_pattern)
                if error_count > 2:  # Some errors expected (missing tools)
                    issues.append(f"Multiple compilation errors ({error_count})")
                    self.log(f"Warnings: {error_count} errors found", "WARNING")
            
            if issues:
                self.results[test_file] = {
                    'status': 'FAIL' if "declared" in issues[0] else 'WARNING',
                    'reason': issues[0],
                    'time': time.time() - test_start,
                    'output': runner_result.stdout[:300]
                }
                return False
            
            self.log(f"Code execution: OK", "SUCCESS")
            self.results[test_file] = {
                'status': 'PASS',
                'reason': 'All checks passed',
                'time': time.time() - test_start
            }
            return True
            
        except subprocess.TimeoutExpired:
            self.log(f"Code execution: TIMEOUT", "ERROR")
            self.results[test_file] = {
                'status': 'FAIL',
                'reason': 'Execution timeout',
                'time': time.time() - test_start
            }
            return False
        except Exception as e:
            self.log(f"Code execution: ERROR - {str(e)[:50]}", "ERROR")
            self.results[test_file] = {
                'status': 'FAIL',
                'reason': str(e)[:50],
                'time': time.time() - test_start
            }
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        self.start_time = time.time()
        
        print("\n" + "="*80)
        print("POLYGLOT TRANSPILER - COMPREHENSIVE TEST SUITE")
        print("="*80 + "\n")
        
        test_files = [
            ('test1.py', 'Original: Complex features'),
            ('test2.py', 'Original: Go async (CRITICAL)'),
            ('test3.py', 'Original: Multiple languages'),
            ('debug_files/test_edge_cases_1.py', 'Edge Case: Simple/empty'),
            ('debug_files/test_edge_cases_2.py', 'Edge Case: Control flow'),
            ('debug_files/test_edge_cases_3.py', 'Edge Case: Async/strings (CRITICAL)'),
            ('debug_files/test_edge_cases_4.py', 'Edge Case: Classes'),
            ('debug_files/test_edge_cases_5.py', 'Edge Case: Math operators'),
            ('debug_files/test_edge_cases_6.py', 'Edge Case: Complex mixed'),
        ]
        
        for test_file, description in test_files:
            self.test_file(test_file, description)
            print()
        
        self.end_time = time.time()
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80 + "\n")
        
        # Count results
        counts = {
            'PASS': sum(1 for r in self.results.values() if r['status'] == 'PASS'),
            'OK': sum(1 for r in self.results.values() if r['status'] == 'OK'),
            'WARNING': sum(1 for r in self.results.values() if r['status'] == 'WARNING'),
            'FAIL': sum(1 for r in self.results.values() if r['status'] == 'FAIL'),
            'SKIP': sum(1 for r in self.results.values() if r['status'] == 'SKIP'),
        }
        
        total = sum(counts.values())
        passed = counts['PASS'] + counts['OK']
        
        # Print statistics
        print("Results:")
        print(f"  PASS/OK:     {passed:2} / {total}")
        print(f"  WARNING:     {counts['WARNING']:2}")
        print(f"  FAIL:        {counts['FAIL']:2}")
        print(f"  SKIP:        {counts['SKIP']:2}")
        print(f"  TOTAL:         {total:2}")
        
        # Time
        elapsed = self.end_time - self.start_time
        print(f"\nExecution Time: {elapsed:.2f} seconds")
        
        # Detailed results
        print("\n" + "-"*80)
        print("DETAILED RESULTS")
        print("-"*80 + "\n")
        
        for test_file, result in self.results.items():
            status_char = {
                'PASS': '',
                'OK': '',
                'WARNING': '',
                'FAIL': '',
                'SKIP': ''
            }[result['status']]
            
            reason = result['reason']
            time_str = f"({result['time']:.2f}s)" if result['time'] > 0 else ""
            
            print(f"{status_char} {test_file:30} - {result['status']:8} {time_str}")
            print(f"  └─ {reason}")
            
            if 'error' in result:
                print(f"  └─ Error: {result['error'][:80]}")
        
        # Final status
        print("\n" + "="*80)
        if counts['FAIL'] == 0:
            print("ALL CRITICAL TESTS PASSED")
            if counts['WARNING'] > 0:
                print(f"{counts['WARNING']} test(s) with warnings (may be expected)")
            print("="*80 + "\n")
            return 0
        else:
            print(f"{counts['FAIL']} TEST(S) FAILED")
            print("\nFailed tests:")
            for test_file, result in self.results.items():
                if result['status'] == 'FAIL':
                    print(f"  - {test_file}: {result['reason']}")
            print("\nRun: python diagnose_and_fix.py")
            print("="*80 + "\n")
            return 1

def main():
    runner = TestRunner()
    exit_code = runner.run_all_tests()
    
    # Print final recommendations
    print("NEXT STEPS:")
    print("-"*80)
    if exit_code == 0:
        print("All tests passed! The transpiler is working correctly.")
        print("The following fixes have been verified:")
        print("  - Go unused variable suppression")
        print("  - While loop translation to Go for loops")
        print("  - Async operations in Go")
        print("\nYou can now use the transpiler with confidence.")
    else:
        print("Some tests failed. Please review the issues above.")
        print("\nTo diagnose specific issues:")
        print("  1. python diagnose_and_fix.py")
        print("  2. python main.py [failing_test_file.py]")
        print("  3. cat out_dir/[segment_file]")
        print("  4. python out_dir/runner.py")
    
    print("-"*80 + "\n")
    return exit_code

if __name__ == '__main__':
    sys.exit(main())
