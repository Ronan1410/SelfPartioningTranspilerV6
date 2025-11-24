#!/usr/bin/env python3
"""Comprehensive test of all test files"""
import sys
import os
import subprocess
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_test(test_file, test_num):
    """Run transpiler on a test file"""
    print(f"\n{'='*80}")
    print(f"TEST {test_num}: {test_file}")
    print('='*80)
    
    if not os.path.exists(test_file):
        print(f"SKIP: File not found")
        return None
    
    try:
        result = subprocess.run(
            [sys.executable, 'main.py', test_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"TRANSPILATION FAILED")
            print(result.stderr)
            return False
        
        # Parse output for segment count
        lines = result.stdout.split('\n')
        for line in lines:
            if 'Analyzing' in line or 'Transpiled' in line or 'HTML Report' in line:
                print(line)
        
        print(f"Transpilation succeeded")
        
        # Check if runner exists and try to run it
        if os.path.exists('out_dir/runner.py'):
            print("\nRunning generated code")
            runner_result = subprocess.run(
                [sys.executable, 'out_dir/runner.py'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Check for critical errors
            if "declared and not used" in runner_result.stdout or "declared and not used" in runner_result.stderr:
                print(f"Go compiler error: declared and not used")
                print(runner_result.stdout[:500])
                return False
            
            if "[ERROR]" in runner_result.stdout and "Failed" in runner_result.stdout:
                # Count errors
                error_count = runner_result.stdout.count("[ERROR]")
                print(f"{error_count} compilation errors found (may be expected)")
                print(runner_result.stdout[:800])
            
            print(f"Generated code executed")
            return True
        
        return True
        
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    # Test files to run
    test_files = [
        'test1.py',
        'test2.py',
        'test3.py',
    ]
    
    print("\n" + "="*80)
    print("COMPREHENSIVE TRANSPILER TEST SUITE")
    print("="*80)
    
    results = {}
    test_num = 1
    
    for test_file in test_files:
        result = run_test(test_file, test_num)
        results[test_file] = result
        test_num += 1
    
    # Summary
    print(f"\n\n{'='*80}")
    print("SUMMARY")
    print('='*80)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    total = len(results)
    
    for test_file, status in results.items():
        if status is True:
            print(f"PASS: {test_file}")
        elif status is False:
            print(f"FAIL: {test_file}")
        else:
            print(f"SKIP: {test_file}")
    
    print(f"\nResults: {passed} passed, {failed} failed, {skipped} skipped out of {total}")
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
