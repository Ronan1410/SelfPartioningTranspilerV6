#!/usr/bin/env python3
"""
Test if compilers are properly installed and accessible.
"""

import subprocess
import shutil
import os
import tempfile

def test_compiler(cmd, test_code, file_ext):
    """Test if a compiler works."""
    print(f"\nTesting {cmd.split()[0]}...", end=" ", flush=True)
    
    # Check if in PATH
    tool = cmd.split()[0]
    path = shutil.which(tool)
    if not path:
        print(f"✗ NOT FOUND in PATH")
        return False
    
    print(f"✓ Found at {path}")
    
    # Try to compile test code
    with tempfile.NamedTemporaryFile(mode='w', suffix=file_ext, delete=False) as f:
        f.write(test_code)
        temp_file = f.name
    
    try:
        exe_file = temp_file.replace(file_ext, '.exe' if os.name == 'nt' else '')
        compile_cmd = cmd.replace('INPUT', temp_file).replace('OUTPUT', exe_file)
        
        print(f"  Compiling test code...", end=" ", flush=True)
        result = subprocess.run(compile_cmd, shell=True, capture_output=True, timeout=10)
        
        if result.returncode == 0:
            print("✓ Compilation successful")
            return True
        else:
            print("✗ Compilation failed")
            if result.stderr:
                print(f"    Error: {result.stderr.decode()[:100]}")
            return False
    except subprocess.TimeoutExpired:
        print("✗ Timeout")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    finally:
        try:
            os.remove(temp_file)
            if os.path.exists(exe_file):
                os.remove(exe_file)
        except:
            pass

def main():
    print("=" * 80)
    print("COMPILER DIAGNOSTIC TEST")
    print("=" * 80)
    
    tests = [
        {
            "name": "Rust (rustc)",
            "cmd": "rustc INPUT -o OUTPUT",
            "code": "fn main() { println!(\"test\"); }",
            "ext": ".rs"
        },
        {
            "name": "C++ (g++)",
            "cmd": "g++ INPUT -o OUTPUT",
            "code": "#include <iostream>\nint main() { std::cout << \"test\"; return 0; }",
            "ext": ".cpp"
        },
        {
            "name": "Go (go)",
            "cmd": "go run INPUT",
            "code": "package main\nfunc main() { println(\"test\") }",
            "ext": ".go"
        },
        {
            "name": "Java (javac)",
            "cmd": "javac INPUT",
            "code": "public class Main { public static void main(String[] args) {} }",
            "ext": ".java"
        }
    ]
    
    results = {}
    for test in tests:
        success = test_compiler(test["cmd"], test["code"], test["ext"])
        results[test["name"]] = success
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    for name, success in results.items():
        status = "✓ OK" if success else "✗ FAILED"
        print(f"  {name:<30} {status}")
    
    print()
    working = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Working compilers: {working}/{total}")
    
    if working == 0:
        print("\n⚠ No compilers found! Install at least one:")
        print("  Rust:  https://rustup.rs/")
        print("  C++:   MinGW (https://www.mingw-w64.org/) or MSVC")
        print("  Go:    https://golang.org/")
        print("  Java:  https://www.oracle.com/java/")
    elif working < total:
        print(f"\n⚠ Some compilers missing ({total - working} not working)")
        print("  Install the missing ones for better results")
    else:
        print("\n✓ All compilers working! profiler should work.")

if __name__ == '__main__':
    main()
