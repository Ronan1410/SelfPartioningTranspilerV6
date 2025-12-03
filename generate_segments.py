#!/usr/bin/env python3
"""Generate segments using the transpiler"""
import sys
import os
import ast

sys.path.insert(0, os.getcwd())

from src.polyglot import PolyglotTranspiler

# Read test file
with open("debug_files/test_comprehensive_new.py", "r") as f:
    source_code = f.read()

tree = ast.parse(source_code)

# Extract functions and classes
segments = []
for i, node in enumerate(tree.body):
    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
        segment_code = ast.get_source_segment(source_code, node)
        if segment_code:
            seg_type = "class" if isinstance(node, ast.ClassDef) else "function"
            segments.append({
                "code": segment_code,
                "type": seg_type,
                "name": node.name,
                "index": len([s for s in segments if s["type"] == seg_type])
            })

# Language mapping
LANG_MAP = {
    "matrix_multiply": "Rust",
    "prime_checker": "Rust",
    "fibonacci_sequence": "C++",
    "merge_sorted_arrays": "Rust",
    "calculate_statistics": "Rust",
    "process_csv_data": "Go",
    "string_processor": "Go",
    "DataAnalyzer": "Java",
    "BankAccount": "Java"
}

# Create output directory
os.makedirs("out_dir", exist_ok=True)

# Transpile each segment
segment_counter = 0
for seg in segments:
    lang = LANG_MAP.get(seg["name"], "Rust")
    
    print(f"Transpiling segment {segment_counter}: {seg['name']} to {lang}")
    
    try:
        transpiled = PolyglotTranspiler.transpile(seg["code"], lang)
        
        # Write to file
        ext_map = {"Rust": "rs", "C++": "cpp", "Go": "go", "Java": "java"}
        ext = ext_map.get(lang, "txt")
        
        lang_label = lang.replace("+", "")  # C++ -> C
        filename = f"out_dir/segment_{segment_counter}_{lang_label}.{ext}"
        
        with open(filename, "w") as f:
            f.write(transpiled)
        
        print(f"  -> {filename}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    segment_counter += 1

print(f"\nGenerated {segment_counter} segments in out_dir/")
