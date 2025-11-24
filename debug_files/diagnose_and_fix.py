#!/usr/bin/env python3
"""
Diagnose issues and suggest/apply fixes
"""
import sys
import os
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def diagnose_specific_test(test_file):
    """Run a specific test and diagnose issues"""
    print(f"\n{'='*80}")
    print(f"DIAGNOSING: {test_file}")
    print('='*80)
    
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        return False
    
    # Show file size and preview
    size = os.path.getsize(test_file)
    with open(test_file, 'r') as f:
        content = f.read()
    
    print(f"\nFile: {test_file}")
    print(f"Size: {size} bytes")
    print(f"Preview (first 300 chars):\n{content[:300]}...")
    
    # Run transpiler
    print(f"\n--- Running Transpiler ---")
    result = subprocess.run(
        [sys.executable, 'main.py', test_file],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode != 0:
        print(f"Transpilation failed")
        print(f"Return code: {result.returncode}")
        print(f"\nError output:\n{result.stderr}")
        return False
    
    print("Transpilation succeeded")
    
    # Check generated files
    print(f"\n--- Checking Generated Files ---")
    if not os.path.exists('out_dir'):
        print("out_dir not created")
        return False
    
    files = os.listdir('out_dir')
    print(f"Generated {len(files)} files:")
    for f in files:
        path = os.path.join('out_dir', f)
        size = os.path.getsize(path)
        print(f"  {f} ({size} bytes)")
    
    # Try to run generated code
    print(f"\n--- Running Generated Code ---")
    if not os.path.exists('out_dir/runner.py'):
        print("No runner.py generated")
        return True
    
    runner_result = subprocess.run(
        [sys.executable, 'out_dir/runner.py'],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    # Check for critical issues
    issues = []
    
    if "declared and not used" in runner_result.stdout:
        issues.append({
            'type': 'Go compiler error',
            'message': 'Variable declared but not used',
            'location': 'Go transpilation',
            'fix': 'Check GoTranspiler.visit_Assign() - should suppress unused vars'
        })
    
    if "error" in runner_result.stderr.lower():
        lines = runner_result.stderr.split('\n')
        for line in lines:
            if 'error' in line.lower():
                issues.append({
                    'type': 'Compilation error',
                    'message': line,
                    'location': 'Code generation',
                    'fix': 'Check relevant transpiler for this language'
                })
    
    # Show output snippet
    output = runner_result.stdout[:800]
    print(f"Output:\n{output}")
    
    if issues:
        print(f"\n{len(issues)} Issue(s) Found:\n")
        for issue in issues:
            print(f"  Type: {issue['type']}")
            print(f"  Message: {issue['message']}")
            print(f"  Location: {issue['location']}")
            print(f"  Suggested Fix: {issue['fix']}")
            print()
        return False
    else:
        print("\nNo critical issues detected")
        return True

def main():
    print("\n" + "="*80)
    print("DIAGNOSTIC TOOL - Debug and Fix Issues")
    print("="*80)
    
    # Test the most likely problem files
    test_files = [
            'test1.py',
            'test2.py',
            'test3.py',
            'debug_files/test_edge_cases_1.py',
            'debug_files/test_edge_cases_2.py',
            'debug_files/test_edge_cases_3.py',
            'debug_files/test_edge_cases_4.py',
            'debug_files/test_edge_cases_5.py',
            'debug_files/test_edge_cases_6.py',
        ]
    
    results = {}
    for test_file in test_files:
        try:
            results[test_file] = diagnose_specific_test(test_file)
        except Exception as e:
            print(f"Error diagnosing {test_file}: {e}")
            results[test_file] = False
    
    # Summary
    print(f"\n\n{'='*80}")
    print("DIAGNOSTIC SUMMARY")
    print('='*80)
    
    for test_file, passed in results.items():
        status = "OK" if passed else "ISSUE"
        print(f"{status}: {test_file}")
    
    return 0 if all(results.values()) else 1

if __name__ == '__main__':
    sys.exit(main())
