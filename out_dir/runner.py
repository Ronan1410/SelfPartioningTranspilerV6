import os
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
        {'file': 'segment_0_Rust.rs', 'lang': 'Rust'},
        {'file': 'segment_1_Cpp.cpp', 'lang': 'C++'},
        {'file': 'segment_2_Go.go', 'lang': 'Go'},
        {'file': 'segment_3_Java.java', 'lang': 'Java'},
    ]

    for i, seg in enumerate(segments):
        filename = seg['file']
        lang = seg['lang']
        print(f"\n>>> Running Segment {i} ({lang}: {filename})")
        
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
