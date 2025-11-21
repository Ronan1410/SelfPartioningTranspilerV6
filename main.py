import ast
import click
import os
import sys

# Ensure src is in path
sys.path.append(os.getcwd())

from src.analyzer import FeatureAnalyzer
from src.decision_engine import DecisionEngine
from src.neural_classifier import NeuralClassifier
from src.polyglot import PolyglotTranspiler
from src.visualizer import Visualizer
from src.html_visualizer import HtmlVisualizer

def _generate_runner(path, segments):
    """
    Generates a Python script that compiles and runs the polyglot segments in order.
    """
    content = """import os
import subprocess
import sys
import time
import shutil

def run_command(cmd):
    print(f"[CMD] {cmd}")
    
    # Extract the executable name (first part of command)
    executable = cmd.split()[0]
    if not shutil.which(executable):
        print(f"[SKIP] Tool '{executable}' not found in PATH. Skipping segment.")
        return False

    try:
        # Run without shell=True for better compatibility/security on Windows
        # We need to split the command into args if it's a string
        if isinstance(cmd, str):
            import shlex
            # shlex.split handles quotes correctly, but on Windows path backslashes can be tricky.
            # Simple split might be enough for our simple commands, but let's use shlex with posix=False for Windows
            args = shlex.split(cmd, posix=(os.name != 'nt'))
        else:
            args = cmd
            
        subprocess.check_call(args)
        return True
    except subprocess.CalledProcessError:
        print(f"[ERROR] Failed to run: {cmd}")
        return False
    except FileNotFoundError:
        print(f"[ERROR] Command not found/executable missing.")
        return False
    except PermissionError:
        print(f"[ERROR] Permission denied. (Do you have the compiler installed/access rights?)")
        return False
    except OSError as e:
        print(f"[ERROR] System error: {e}")
        return False

def main():
    print("--- Polyglot Execution Runner ---")
    
    # Diagnostic: Check PATH and compilers
    print(f"[DEBUG] PATH environment variable length: {len(os.environ.get('PATH', ''))}")
    for tool in ['rustc', 'g++', 'go', 'java', 'javac']:
        path = shutil.which(tool)
        if path:
            print(f"[DEBUG] Found {tool} at: {path}")
        else:
            print(f"[WARNING] Could not find '{tool}' in PATH.")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    
    segments = [
"""
    for seg in segments:
        content += f"        {{'file': '{seg['file']}', 'lang': '{seg['lang']}'}},\n"
        
    content += """    ]

    for i, seg in enumerate(segments):
        filename = seg['file']
        lang = seg['lang']
        print(f"\\n>>> Running Segment {i} ({lang}: {filename})")
        
        if lang == "Rust":
            # rustc filename.rs -o filename.exe && ./filename.exe
            exe_name = filename.replace('.rs', '.exe' if os.name == 'nt' else '')
            compile_cmd = f"rustc {filename} -o {exe_name}"
            run_cmd = f".{os.sep}{exe_name}" if os.name != 'nt' else exe_name
            
            if run_command(compile_cmd):
                run_command(run_cmd)
                
        elif lang == "C++":
            # g++ filename.cpp -o filename.exe && ./filename.exe
            exe_name = filename.replace('.cpp', '.exe' if os.name == 'nt' else '')
            compile_cmd = f"g++ {filename} -o {exe_name}"
            run_cmd = f".{os.sep}{exe_name}" if os.name != 'nt' else exe_name
            
            if run_command(compile_cmd):
                run_command(run_cmd)

        elif lang == "Go":
            # go run filename.go
            run_command(f"go run {filename}")

        elif lang == "Java":
            # javac filename.java && java ClassName
            # Assuming class name is Main or filename dependent. 
            # My PolyglotTranspiler uses 'public class Main' or similar.
            # If multiple files have 'class Main', this will clash.
            # For this mock, let's assume single file compilation or just printing.
            
            # Note: The Mock Polyglot output for Java is 'public class Main'.
            # We need to rename the file to Main.java to compile it properly in Java,
            # OR we should have generated it as Main.java.
            # But we have segment_i_Java.java.
            # Quick hack: Rename temporarily or just try to run single-file source-code mode (Java 11+)
            
            run_command(f"java {filename}")

        else:
            print(f"Unknown language: {lang}")
            
        time.sleep(0.5)

if __name__ == "__main__":
    main()
"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

@click.command()
@click.argument('input_file', type=click.Path(exists=True))
def main(input_file):
    """
    Polyglot Transpiler v1.
    
    Analyzes Python code and splits it into [Rust, C++, Go, Java] based on 
    mathematical cost functions and neural network predictions.
    """
    click.echo(f"Analyzing {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        source_code = f.read()
        
    # 1. Parse and Split (Naive split by function for this demo)
    tree = ast.parse(source_code)
    
    segments = []
    
    # Extract functions and classes as segments
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            segment_code = ast.get_source_segment(source_code, node)
            # Determine type label
            seg_type = "class" if isinstance(node, ast.ClassDef) else "function"
            segments.append({"ast": node, "code": segment_code, "type": seg_type})
        # Handle top-level code? For now, ignore or treat as main block.
        
    if not segments:
        click.echo("No functions found. Treating whole file as one segment.")
        segments.append({"ast": tree, "code": source_code, "type": "module"})

    # 2. Analyze & Decide
    analyzer = FeatureAnalyzer()
    decision_engine = DecisionEngine(use_neural_fallback=True)
    neural_net = NeuralClassifier()
    
    results = []
    
    for seg in segments:
        # Extract features
        features = analyzer.analyze(seg["ast"])
        
        # Cost Function Decision
        decision = decision_engine.decide(features)
        
        if decision is None:
            # Inconclusive -> Neural Net
            click.secho(f"Cost function inconclusive for segment. Using Neural Network...", fg="yellow")
            # Vectorize features for NN: [math, io, loops, conditionals, functions, classes, async, recursion, strings]
            vec = [
                features.math_ops, features.io_ops, features.loops, 
                features.conditionals, features.functions, features.classes,
                features.async_ops, int(features.recursion), features.string_ops
            ]
            best_lang, _ = neural_net.predict(vec)
            score = 0.0 # NN doesn't return cost score same way
            source = "NeuralNet"
        else:
            best_lang, scores_map = decision
            score = scores_map[best_lang]
            source = "CostFunction"
            
        # Transpile
        transpiled_code = PolyglotTranspiler.transpile(seg["code"], best_lang)
        
        results.append({
            "features": features,
            "lang": best_lang,
            "score": score,
            "source": source,
            "original": seg["code"],
            "transpiled": transpiled_code
        })

    # 3. Output Code
    # Ensure output directory exists
    output_dir = "out_dir"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    segment_files = []

    for i, res in enumerate(results):
        ext_map = {"Rust": "rs", "C++": "cpp", "Go": "go", "Java": "java"}
        ext = ext_map.get(res['lang'], "txt")
        # C++ file extension should be .cpp, output filename segment_1_Cpp.cpp to correspond with runner expectation
        lang_label = res['lang']
        if lang_label == "C++":
             lang_label = "Cpp"
        
        filename = f"segment_{i}_{lang_label}.{ext}"
        out_path = os.path.join(output_dir, filename)
        
        with open(out_path, 'w') as f:
            f.write(res['transpiled'])
            
        segment_files.append({
            "file": filename,
            "lang": res['lang']
        })
    
    click.echo(f"Transpiled segments written to '{output_dir}/' directory.")
    
    # Generate Runner Script
    runner_path = os.path.join(output_dir, "runner.py")
    _generate_runner(runner_path, segment_files)
    click.echo(f"Runner script generated at '{runner_path}'.")

    # 4. Visualize
    # Terminal Summary
    viz = Visualizer()
    viz.print_summary(results)
    
    # HTML Report (Robust, no Graphviz dependency)
    html_viz = HtmlVisualizer(output_dir="viz")
    report_path = html_viz.generate_report(results)
    click.echo(f"HTML Report generated: {report_path}")
    
    # Graphviz (Optional fallback)
    try:
        graph_path = viz.generate_flow_graph(results)
        click.echo(f"PDF Graph generated: {graph_path}.pdf")
    except Exception:
        pass # Silent fail if Graphviz missing, user has HTML now

if __name__ == '__main__':
    main()
