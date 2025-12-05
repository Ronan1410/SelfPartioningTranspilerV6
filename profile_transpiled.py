#!/usr/bin/env python3
"""
Profile and compare execution performance of original Python code vs transpiled segments.
Measures speed, memory, and execution efficiency gains.

Usage: python profile_transpiled.py test_file.py
"""

import ast
import os
import sys
import time
import psutil
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.append(os.getcwd())

from src.analyzer import FeatureAnalyzer
from src.decision_engine import DecisionEngine
from src.neural_classifier import NeuralClassifier
from src.polyglot import PolyglotTranspiler

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class ExecutionProfiler:
    """Profile and compare code execution performance."""
    
    def __init__(self, input_file: str):
        self.input_file = input_file
        self.source_code = ""
        self.results = []
        
        with open(input_file, 'r', encoding='utf-8') as f:
            self.source_code = f.read()
    
    def profile_python_execution(self) -> Dict:
        """Execute original Python code and measure performance."""
        print("Profiling original Python code...", end=" ", flush=True)
        
        result = {
            "language": "Python (Original)",
            "compiled": False,
            "status": "unknown",
        }
        
        try:
            # Capture output
            import io
            from contextlib import redirect_stdout, redirect_stderr
            
            # Measure execution time and memory
            process = psutil.Process(os.getpid())
            
            # Warm up
            exec(self.source_code, {"__name__": "__main__"})
            
            # Actual measurement with output capture
            mem_before = process.memory_info().rss / 1024 / 1024
            start_time = time.perf_counter()
            
            output_buffer = io.StringIO()
            with redirect_stdout(output_buffer):
                exec(self.source_code, {"__name__": "__main__"})
            
            elapsed = time.perf_counter() - start_time
            mem_after = process.memory_info().rss / 1024 / 1024
            
            output = output_buffer.getvalue()
            
            result.update({
                "total_time_ms": elapsed * 1000,
                "memory_delta_mb": max(0, mem_after - mem_before),
                "status": "success",
                "output": output
            })
            print(f"✓ ({result['total_time_ms']:.2f}ms)")
            
        except Exception as e:
            result["status"] = f"error: {str(e)}"
            print(f"✗ ({result['status']})")
        
        return result
    
    def transpile_and_profile(self) -> List[Dict]:
        """Transpile code and profile each segment."""
        try:
            tree = ast.parse(self.source_code)
        except SyntaxError as e:
            print(f"Error parsing {self.input_file}: {e}")
            return []
        
        # Extract segments
        segments = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                segment_code = ast.get_source_segment(self.source_code, node)
                segments.append({
                    "ast": node,
                    "code": segment_code,
                    "name": node.name,
                    "type": "class" if isinstance(node, ast.ClassDef) else "function"
                })
        
        if not segments:
            segments.append({
                "ast": tree,
                "code": self.source_code,
                "name": "module",
                "type": "module"
            })
        
        # Analyze and transpile
        analyzer = FeatureAnalyzer()
        decision_engine = DecisionEngine(use_neural_fallback=True)
        neural_net = NeuralClassifier()
        
        transpiled_results = []
        
        for i, seg in enumerate(segments):
            features = analyzer.analyze(seg["ast"])
            decision = decision_engine.decide(features)
            
            if decision is None:
                vec = [
                    features.math_ops, features.io_ops, features.loops,
                    features.conditionals, features.functions, features.classes,
                    features.async_ops, int(features.recursion), features.string_ops
                ]
                best_lang, _ = neural_net.predict(vec)
            else:
                best_lang, _ = decision
            
            transpiled_code = PolyglotTranspiler.transpile(seg["code"], best_lang)
            
            # Profile transpiled code
            profile_result = self._profile_transpiled_segment(
                best_lang, transpiled_code, i
            )
            
            profile_result["segment_index"] = i
            profile_result["segment_name"] = seg["name"]
            transpiled_results.append(profile_result)
        
        return transpiled_results
    
    def _wrap_for_execution(self, code: str, language: str) -> str:
        """Wrap transpiled code to make it compilable/executable.
        Code from the transpiler usually already has main functions, so we just return as-is."""
        
        # The transpiler already generates complete, executable code with main functions
        # Just return it as-is. The transpiler handles all the wrapping.
        return code
    
    def _profile_transpiled_segment(self, language: str, code: str, index: int) -> Dict:
        """Profile a single transpiled segment."""
        print(f"Profiling segment {index} ({language})...", end=" ", flush=True)
        
        # Wrap code to make it compilable
        code = self._wrap_for_execution(code, language)
        
        result = {
            "language": language,
            "compiled": False,
            "status": "unknown",
        }
        
        # Create temporary file
        ext_map = {"Rust": "rs", "C++": "cpp", "Go": "go", "Java": "java"}
        ext = ext_map.get(language, "txt")
        
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f"transpile_{index}_{int(time.time()*1000)}.{ext}")
        
        with open(temp_file, 'w') as f:
            f.write(code)
        
        # Also save to out_dir for debugging
        debug_dir = Path("out_dir")
        debug_dir.mkdir(exist_ok=True)
        debug_file = debug_dir / f"segment_{index}_{language}.{ext}"
        with open(debug_file, 'w') as f:
            f.write(code)
        
        try:
            compile_args = None
            run_args = None
            exe_file = None
            
            if language == "Rust":
                exe_file = temp_file.replace('.rs', '.exe' if os.name == 'nt' else '')
                compile_args = ["rustc", temp_file, "-o", exe_file, "-O"]
                run_args = [exe_file]
                
            elif language == "C++":
                exe_file = temp_file.replace('.cpp', '.exe' if os.name == 'nt' else '')
                compile_args = ["g++", temp_file, "-o", exe_file, "-O3"]
                run_args = [exe_file]
                
            elif language == "Go":
                exe_file = temp_file.replace('.go', '.exe' if os.name == 'nt' else '')
                compile_args = ["go", "build", "-o", exe_file, temp_file]
                run_args = [exe_file]
                
            elif language == "Java":
                class_name = "Main"
                exe_file = temp_file.replace('.java', '')
                compile_args = ["javac", temp_file]
                run_args = ["java", "-cp", str(Path(temp_file).parent), class_name]
            
            # Try to compile if needed
            if compile_args:
                try:
                    result_compile = subprocess.run(compile_args, capture_output=True, 
                                                   timeout=10, check=False)
                    if result_compile.returncode != 0:
                        error_msg = result_compile.stderr.decode() if result_compile.stderr else result_compile.stdout.decode() if result_compile.stdout else "unknown error"
                        result["status"] = f"compile_error"
                        result["error_detail"] = error_msg[:200]  # Store first 200 chars of error
                        print(f"✗ (compilation failed: {error_msg[:80]})")
                        return result
                    result["compiled"] = True
                except subprocess.TimeoutExpired:
                    result["status"] = "compile_timeout"
                    print(f"✗ (compilation timeout)")
                    return result
                except Exception as e:
                    result["status"] = f"compile_error"
                    result["error_detail"] = str(e)[:200]
                    print(f"✗ (compilation failed: {str(e)[:80]})")
                    return result
            
            # Execute and measure
            if run_args:
                try:
                    # Run multiple times to get average execution time (excluding startup overhead)
                    runs = 5
                    times = []
                    
                    for i in range(runs):
                        start_time = time.perf_counter()
                        proc = subprocess.run(run_args, capture_output=True, timeout=5, check=False)
                        elapsed = time.perf_counter() - start_time
                        times.append(elapsed)
                        
                        # Check for errors on first run
                        if i == 0 and proc.returncode != 0:
                            error_msg = proc.stderr.decode() if proc.stderr else "unknown error"
                            result["status"] = "execution_error"
                            result["error_detail"] = error_msg[:200]
                            print(f"✗ (execution failed: {error_msg[:80]})")
                            break
                    
                    if result["status"] != "execution_error":
                        # Use average of all runs
                        avg_elapsed = sum(times) / len(times)
                        
                        result.update({
                            "total_time_ms": avg_elapsed * 1000,
                            "memory_delta_mb": 0,  # Memory tracking disabled during multi-run
                            "status": "success"
                        })
                        print(f"✓ ({result['total_time_ms']:.2f}ms)")
                    
                except subprocess.TimeoutExpired:
                    result["status"] = "timeout"
                    print("✗ (timeout)")
                except Exception as e:
                    result["status"] = f"execution_error"
                    print(f"✗ ({result['status']})")
            
        finally:
            # Cleanup
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                if exe_file and os.path.exists(exe_file):
                    os.remove(exe_file)
            except:
                pass
        
        return result
    
    def run_full_profile(self) -> Tuple[Dict, List[Dict]]:
        """Run complete profiling."""
        print("=" * 80)
        print(f"PROFILING: {self.input_file}")
        print("=" * 80)
        print()
        
        # Profile original Python
        python_result = self.profile_python_execution()
        
        # Profile transpiled versions
        transpiled_results = self.transpile_and_profile()
        
        return python_result, transpiled_results
    
    def print_summary(self, python_result: Dict, transpiled_results: List[Dict]):
        """Print detailed comparison summary."""
        print()
        print("=" * 80)
        print("PERFORMANCE COMPARISON")
        print("=" * 80)
        print()
        
        successful = [r for r in transpiled_results if r["status"] == "success"]
        
        if not successful:
            print("[WARNING] No successful transpilations to compare")
            return
        
        print("PYTHON (ORIGINAL):")
        if python_result["status"] == "success":
            print(f"  Time:   {python_result['total_time_ms']:.2f} ms")
            print(f"  Memory: {python_result['memory_delta_mb']:.2f} MB")
            if "output" in python_result and python_result["output"]:
                print("\n  Output:")
                for line in python_result["output"].strip().split('\n'):
                    print(f"    {line}")
        else:
            print(f"  Status: {python_result['status']}")
        print()
        
        print("TRANSPILED VERSIONS:")
        print()
        print(f"{'Language':<12} {'Time (ms)':<12} {'Speedup':<12} {'Memory (MB)':<12} {'Status':<15}")
        print("-" * 80)
        
        if python_result["status"] == "success":
            python_time = python_result["total_time_ms"]
            
            for result in transpiled_results:
                if result["status"] == "success":
                    trans_time = result["total_time_ms"]
                    speedup = python_time / trans_time
                    
                    status = f"{speedup:.2f}x faster" if speedup > 1 else "slower"
                    color_indicator = "✓" if speedup > 1 else "✗"
                    
                    print(
                        f"{result['language']:<12} {trans_time:<12.2f} "
                        f"{speedup:<12.2f}x {result['memory_delta_mb']:<12.2f} {color_indicator} {status:<10}"
                    )
                else:
                    print(
                        f"{result['language']:<12} {'N/A':<12} {'N/A':<12} {'N/A':<12} "
                        f"✗ {result['status']:<10}"
                    )
        
        print()
        
        # Summary stats
        successful_count = len(successful)
        if successful_count > 0:
            avg_speedup = sum(
                python_result["total_time_ms"] / r["total_time_ms"] 
                for r in successful if python_result["status"] == "success"
            ) / successful_count
            
            if python_result["status"] == "success":
                print(f"Average Speedup: {avg_speedup:.2f}x")
                print(f"Successful Transpilations: {successful_count}/{len(transpiled_results)}")
                print()
                
                if avg_speedup > 1:
                    improvement = (avg_speedup - 1) * 100
                    print(f"✓ Transpilation provides {improvement:.1f}% average speedup")
                elif avg_speedup < 1:
                    slowdown = (1 - avg_speedup) * 100
                    print(f"✗ Transpiled code is {slowdown:.1f}% slower (might be overhead)")
                else:
                    print("≈ Performance is similar to Python")
    
    def save_json(self, python_result: Dict, transpiled_results: List[Dict],
                  output_dir: str = "out_dir"):
        """Save results as JSON."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        filename = Path(self.input_file).stem
        json_file = output_path / f"profile_{filename}.json"
        
        data = {
            "input_file": str(self.input_file),
            "python_original": python_result,
            "transpiled_segments": transpiled_results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return json_file
    
    def generate_charts(self, python_result: Dict, transpiled_results: List[Dict],
                       output_dir: str = "viz"):
        """Generate comparison charts."""
        if not MATPLOTLIB_AVAILABLE:
            print("\n[WARNING] matplotlib not installed. Skipping charts.")
            print("Install with: pip install matplotlib")
            return
        
        successful = [r for r in transpiled_results if r["status"] == "success"]
        if not successful:
            return
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        filename = Path(self.input_file).stem
        
        # Prepare data
        langs = ["Python"] + [r["language"] for r in successful]
        times = [python_result["total_time_ms"] if python_result["status"] == "success" else 0]
        times += [r["total_time_ms"] for r in successful]
        
        memories = [python_result["memory_delta_mb"] if python_result["status"] == "success" else 0]
        memories += [r["memory_delta_mb"] for r in successful]
        
        # Chart 1: Execution Time Comparison
        fig, ax = plt.subplots(figsize=(12, 6))
        colors = ['#FF6B6B'] + ['#45B7D1'] * len(successful)
        bars = ax.bar(langs, times, color=colors, edgecolor='black', alpha=0.7, linewidth=2)
        
        # Add value labels
        for bar, time_val in zip(bars, times):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{time_val:.2f}ms', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax.set_ylabel('Execution Time (milliseconds)', fontsize=12, fontweight='bold')
        ax.set_title('Execution Time: Python vs Transpiled Code', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        chart_file = output_path / f"profile_execution_time_{filename}.png"
        plt.savefig(chart_file, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"\nSaved: {chart_file}")
        
        # Chart 2: Speedup Factor
        if python_result["status"] == "success" and times[0] > 0:
            speedups = [1.0] + [times[0] / t if t > 0 else 0 for t in times[1:]]
            
            fig, ax = plt.subplots(figsize=(12, 6))
            colors_speedup = ['gray'] + ['#90EE90' if s > 1 else '#FFB6C1' for s in speedups[1:]]
            bars = ax.bar(langs, speedups, color=colors_speedup, edgecolor='black', 
                         alpha=0.7, linewidth=2)
            
            # Add 1.0x reference line
            ax.axhline(y=1.0, color='red', linestyle='--', linewidth=2, label='Baseline (Python)')
            
            # Add value labels
            for bar, speedup in zip(bars, speedups):
                height = bar.get_height()
                label = f'{speedup:.2f}x' if speedup != 1.0 else 'Baseline'
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       label, ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            ax.set_ylabel('Speedup Factor', fontsize=12, fontweight='bold')
            ax.set_title('Performance Improvement vs Python', fontsize=14, fontweight='bold')
            ax.set_ylim([0, max(speedups) * 1.2])
            ax.grid(axis='y', alpha=0.3)
            ax.legend()
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            speedup_file = output_path / f"profile_speedup_{filename}.png"
            plt.savefig(speedup_file, dpi=150, bbox_inches='tight')
            plt.close()
            print(f"Saved: {speedup_file}")
        
        # Chart 3: Memory Comparison
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(langs, memories, color=colors, edgecolor='black', alpha=0.7, linewidth=2)
        
        # Add value labels
        for bar, mem_val in zip(bars, memories):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{mem_val:.2f}MB', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax.set_ylabel('Memory Usage (megabytes)', fontsize=12, fontweight='bold')
        ax.set_title('Memory Consumption: Python vs Transpiled Code', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        mem_file = output_path / f"profile_memory_{filename}.png"
        plt.savefig(mem_file, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"Saved: {mem_file}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python profile_transpiled.py <test_file.py>")
        print()
        print("Example:")
        print("  python profile_transpiled.py test1.py")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not Path(input_file).exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    profiler = ExecutionProfiler(input_file)
    python_result, transpiled_results = profiler.run_full_profile()
    
    profiler.print_summary(python_result, transpiled_results)
    
    json_file = profiler.save_json(python_result, transpiled_results)
    print(f"\nSaved JSON: {json_file}")
    
    profiler.generate_charts(python_result, transpiled_results)
    
    print()
    print("=" * 80)
    print("PROFILING COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
