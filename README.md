# SelfPartioningTranspilerV6

A sophisticated polyglot code transpiler that intelligently partitions Python code segments into optimal target languages (Rust, C++, Go, Java) using mathematical cost functions and neural network fallback classification.

## Project Overview

This project solves the problem of **polyglot optimization**: given a Python codebase, how do you decide which segments should be transpiled to which compiled language for maximum performance and readability?

Rather than transpiling entire Python programs to a single target language, this transpiler analyzes individual code segments and makes intelligent decisions about which language is best suited for each segment based on:
- Mathematical cost functions derived from code feature analysis
- Neural network predictions for edge cases
- Comfort balancing to ensure readable segment sizes

### The Vision

Modern software development often requires mixing languages for performance-critical sections. This transpiler automates the decision-making process, allowing developers to:
1. Write prototypes in Python
2. Automatically identify segments suitable for specific languages
3. Generate optimized polyglot code
4. Execute the generated code directly

## How I Came Up With the Cost/Comfort Function

### The Problem Statement

When analyzing code, certain features naturally align with specific languages:
- **Math-heavy operations** → Rust or C++ (compiled languages with optimizations)
- **I/O operations** → Go (excellent concurrency and networking)
- **Object-oriented code** → Java (strong class system)
- **Performance-critical loops** → Rust or C++ (zero-cost abstractions)

### Development Process

1. **Feature Extraction**: First, I implemented a code analyzer (AST walker) that extracts 9 key features from code:
   - `math_ops`: Arithmetic operations
   - `io_ops`: File/network I/O operations  
   - `loops`: For/while loop counts
   - `conditionals`: If/else statements
   - `functions`: Function call counts
   - `classes`: Class definitions
   - `async_ops`: Async/await operations
   - `recursion`: Boolean flag for recursive patterns
   - `string_ops`: String literal counts

2. **Language Suitability Scoring**: Based on language strengths, I assigned weights (0.0 to 1.0+) for each feature:
   - **Rust**: Excellent at math (1.0) and loops (1.0), weak at classes (0.1)
   - **C++**: Best overall with strong math (1.0), recursion (1.0), classes (0.8)
   - **Go**: Perfect for I/O (1.0) and async (1.0), weaker at recursion (0.6)
   - **Java**: Dominant in classes (2.0), strong strings (1.0), moderate math (0.8)

3. **The Comfort Concept**: Beyond cost, I recognized that segment size matters for developer experience:
   - **Minimum lines**: Segments smaller than 5 lines are merged (too fragmented)
   - **Maximum lines**: Segments larger than 50 lines are flagged (hard to read)
   - **Comfort balancing**: Automatically merges adjacent small segments without exceeding max size

### Cost Function Formula

```
COST_SCORE(features, language) = base_cost × 10 
                                  + math_ops × weight_math × 2.0
                                  + io_ops × weight_io × 2.0
                                  + loops × weight_loops × 3.0
                                  + strings × weight_strings × 1.5
                                  + classes × weight_classes × 10.0
                                  + async_ops × weight_async × 5.0
                                  + (recursion ? weight_recursion × 15.0 : 0)
```

**Scoring Logic**:
- Higher scores = better suitability for that language
- The language with the highest score is selected
- If top two scores are within 0.1 (inconclusive), fall back to neural network

**Example**:
```
Code: for i in range(100): sum += i*i

Features: math_ops=2, loops=1, others=0

Rust score:    0.9×10 + 2×1.0×2.0 + 1×1.0×3.0 = 9.0 + 4.0 + 3.0 = 16.0 ✓ SELECTED
C++ score:     0.85×10 + 2×1.0×2.0 + 1×1.0×3.0 = 8.5 + 4.0 + 3.0 = 15.5
Go score:      0.8×10 + 2×0.7×2.0 + 1×0.9×3.0 = 8.0 + 2.8 + 2.7 = 13.5
Java score:    0.7×10 + 2×0.8×2.0 + 1×0.8×3.0 = 7.0 + 3.2 + 2.4 = 12.6
```

## Project Flow and Architecture

### Chronological Processing Steps

The transpiler processes code through a well-defined pipeline:

```
┌─────────────────────────────────────────────────────────────────┐
│ INPUT: Python source file (main.py or test file)                │
└──────────────────────────────┬──────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: PARSING                                                 │
│ - Read source file as text                                      │
│ - Parse into Python AST (Abstract Syntax Tree)                  │
│ - Split into segments by function/class definitions             │
└──────────────────────────────┬──────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: FEATURE ANALYSIS                                        │
│ - For each segment, walk the AST                                │
│ - Extract CodeFeatures (9 dimensions)                           │
│ - Count math ops, I/O calls, loops, classes, etc.               │
│                                                                 │
│ Output: CodeFeatures object with counts for each segment        │
└──────────────────────────────┬──────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: DECISION ENGINE (COST FUNCTION)                         │
│ - Calculate suitability score for all 4 languages               │
│ - Apply feature weights and multipliers                         │
│ - Select language with highest score                            │
│ - If top 2 languages within 0.1 margin → INCONCLUSIVE           │
│                                                                 │
│ Output: (best_language, scores_dict) or None (fallback)         │
└──────────────────────────────┬──────────────────────────────────┘
                               ↓
         ┌─────────────────────┴────────────────────┐
         │                                          │
         ↓ (Conclusive)               ↓ (Inconclusive)
    ┌─────────────────┐         ┌──────────────────┐
    │ USE COST RESULT │         │ NEURAL NETWORK   │
    └────────┬────────┘         └────────┬─────────┘
             │                          │
             └──────────────┬───────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: NEURAL CLASSIFICATION (FALLBACK)                        │
│ - Only triggered if cost function inconclusive                  │
│ - Vectorize features into 9-dim tensor                          │
│ - Pass through 3-layer neural network:                          │
│   - Input layer: 9 → 64 (ReLU)                                  │
│   - Hidden layer: 64 → 32 (ReLU)                                │
│   - Output layer: 32 → 4 (softmax over Rust/C++/Go/Java)        │
│ - Returns predicted language                                    │
│                                                                 │
│ Output: best_language string                                    │
└──────────────────────────────┬──────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: TRANSPILATION                                           │
│ - For each segment and its assigned language:                   │
│   - Create language-specific transpiler                         │
│   - Walk Python AST and generate target language code           │
│   - Handle language-specific patterns:                          │
│     * Rust: Type annotations, ownership, mut keyword            │
│     * C++: Headers, namespaces, type casting                    │
│     * Go: Package structure, simplified syntax, error handling  │
│     * Java: Classes, public/static, type declarations           │
│                                                                 │
│ Output: Generated code for each segment in target language      │
└──────────────────────────────┬──────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: COMFORT BALANCING (Optional)                            │
│ - Merge segments smaller than min_lines (5)                     │
│ - Check merged size doesn't exceed max_lines (50)               │
│ - Ensures readable, cohesive segment sizes                      │
│                                                                 │
│ Output: Rebalanced segment list                                 │
└──────────────────────────────┬──────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 7: CODE GENERATION                                         │
│ - Create out_dir/ directory if not exists                       │
│ - Write each segment to file:                                   │
│   - segment_0_Rust.rs                                           │
│   - segment_1_Cpp.cpp                                           │
│   - segment_2_Go.go                                             │
│   - segment_3_Java.java                                         │
│                                                                 │
│ Output: Language-specific files in out_dir/                     │
└──────────────────────────────┬──────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 8: RUNNER GENERATION                                       │
│ - Generate out_dir/runner.py                                    │
│ - Contains polyglot execution logic:                            │
│   - For Rust: rustc compile, execute .exe                       │
│   - For C++: g++ compile, execute .exe                          │
│   - For Go: go run (no compile step)                            │
│   - For Java: java direct execution                             │
│ - Detects available compilers via shutil.which()                │
│ - Gracefully skips unavailable tools                            │
│                                                                 │
│ Output: runner.py script                                        │
└──────────────────────────────┬──────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 9: VISUALIZATION                                           │
│ - Terminal summary of all segments                              │
│   - Original code, features, scores, language choice            │
│ - HTML report (robust, no dependencies)                         │
│   - Visual breakdown of feature distributions                   │
│   - Decision path for each segment                              │
│ - Optional Graphviz PDF flow diagram                            │
│   - (silently skipped if Graphviz not installed)                │
│                                                                 │
│ Output: viz/ directory with HTML report + optional PDF          │
└──────────────────────────────┬──────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│ OUTPUT: Ready-to-execute polyglot code                          │
│ - out_dir/: Compiled code files                                 │
│ - out_dir/runner.py: Execution harness                          │
│ - viz/: Analysis reports                                        │
└─────────────────────────────────────────────────────────────────┘
```

## Code Processing Details

### Phase 1: AST Parsing and Segmentation
- Uses Python's `ast` module to parse source code
- Identifies top-level functions, classes, and async functions
- Treats each as a separate segment (can be configured for finer granularity)
- Preserves source location info for error reporting

### Phase 2: Feature Extraction (FeatureAnalyzer)
The analyzer walks the entire AST and counts:
- **Mathematical operations**: All `BinOp` nodes (arithmetic, power, etc.)
- **I/O operations**: Calls to `print`, `open`, `read`, `write`, `input`
- **Loops**: Both `For` and `While` nodes
- **Control flow**: `If` statement nodes
- **Functions**: Function call nodes (excluding I/O)
- **Classes**: `ClassDef` nodes
- **Async operations**: `AsyncFunctionDef` nodes
- **Recursion**: Detected by matching function name in calls
- **Strings**: String constants in `Constant` nodes

### Phase 3: Cost-Based Decision Making (DecisionEngine)
1. For each of 4 languages, calculate a suitability score
2. Apply the cost function formula with language-specific weights
3. Return the language with highest score
4. Check "margin" (difference between 1st and 2nd place)
5. If margin < 0.1 and neural fallback enabled, return `None` to trigger fallback

### Phase 4: Neural Network Fallback (NeuralClassifier)
- 3-layer fully-connected neural network
- Input: 9-dimensional feature vector
- Output: 4-way softmax (probability for each language)
- Uses Xavier uniform initialization for stable predictions
- Only invoked when cost function cannot decide confidently

### Phase 5: Transpilation
Each language has its own transpiler class inheriting from `BaseTranspiler`:

**RustTranspiler**:
- Adds `#![allow(warnings)]` header
- Translates variable declarations to `let` with optional `mut`
- Detects reassignment to add `mut` keyword automatically
- Converts Python `for i in range(n)` to Rust `for i in 0..n`
- Handles while loops directly
- Type inference: assumes `i32` for integers
- Handles recursion and return types

**CppTranspiler**:
- Adds standard headers: `iostream`, `cmath`, `vector`
- Declares variables with explicit `int` type
- Generates `main()` function wrapper
- Special handling for known patterns: factorial, fibonacci, power
- Prints results using `cout`

**GoTranspiler**:
- Package declaration and selective imports
- Variable analysis to detect unused variables (suppressed with `_`)
- Converts Python `while` to Go `for`
- Converts Python `for i in range(n)` to Go C-style `for i := 0; i < n; i++`
- Special handling for `time.Sleep()` and async operations
- F-string to `fmt.Printf` conversion
- No explicit type declarations (uses `:=` inference)

**JavaTranspiler**:
- Wraps code in `public class Main`
- Converts Python classes to Java static nested classes
- Generates `main()` method for execution
- Handles method calls and field access with `this.`
- String operations converted to Java equivalents (`toUpperCase()`, `String.valueOf()`)

### Phase 6: Comfort Balancing (ComfortBalancer)
- Merges segments smaller than 5 lines into adjacent segments
- Ensures merged segments don't exceed 50 lines
- Preserves segment metadata (tags, IDs)
- Maintains logical code grouping

### Phase 7: File Generation
- Creates output directory structure
- Writes each segment to a language-specific file
- Filename format: `segment_{index}_{Language}.{extension}`
- Extensions: `.rs`, `.cpp`, `.go`, `.java`

### Phase 8: Runner Script Generation
- Creates Python script that orchestrates compilation and execution
- For each segment:
  - **Rust**: `rustc filename.rs -o filename.exe && ./filename.exe`
  - **C++**: `g++ filename.cpp -o filename.exe && ./filename.exe`
  - **Go**: `go run filename.go`
  - **Java**: `java filename`
- Cross-platform support (Windows vs. Linux path handling)
- Graceful degradation: skips segments if compiler not found

### Phase 9: Visualization and Reporting
1. **Terminal Summary** (Visualizer):
   - Prints each segment's features, original code, transpiled code
   - Shows decision source (CostFunction vs. NeuralNet)

2. **HTML Report** (HtmlVisualizer):
   - Creates `viz/report.html`
   - Visual bar charts of feature distributions
   - Decision justification for each segment
   - Side-by-side code comparison

3. **PDF Graph** (Optional):
   - Graphviz DOT format flowchart
   - Shows decision path and transpilation results

## Key Design Decisions

### 1. Two-Tier Decision Making
- **Cost function**: Fast, interpretable, rule-based
- **Neural network**: Fallback for edge cases, learns implicit patterns
- This hybrid approach balances speed and accuracy

### 2. Language-Specific Transpilers
- Separate AST visitor for each language
- Handles language quirks explicitly
- Easier to maintain and extend than a unified transpiler

### 3. Comfort Balancing
- Recognizes that performance optimization isn't the only goal
- Developer readability matters for maintainability
- Balancing prevents creating hundreds of tiny fragments

### 4. Cross-Platform Support
- Uses `shutil.which()` to detect available tools
- Custom command parsing for Windows vs. POSIX
- Graceful skipping of unavailable compilers

### 5. Feature Extraction Simplicity
- Counts features rather than complex semantic analysis
- Trades precision for speed and simplicity
- Sufficient for common patterns

## Usage

### Quick Start
```bash
# Transpile a test file
python main.py test_polyglot_2.py

# Run the generated code
python out_dir/runner.py

# View HTML report
open viz/report.html
```

### Detailed Workflow
```bash
# 1. Write or select a Python file
# 2. Analyze it
python main.py your_file.py

# 3. Check generated code
ls out_dir/
cat out_dir/segment_0_Rust.rs

# 4. Compile and run
python out_dir/runner.py

# 5. Review analysis
open viz/report.html
```

## Testing

```bash
# Run comprehensive test suite
python debug_files/run_comprehensive_tests.py

# Validate all fixes
python validate_all.py

# Inspect specific generation
python inspect_generation.py

# Test Go transpilation only
python manual_go_test.py
```

See `TESTING_GUIDE.md` for detailed testing documentation.

## Recent Fixes

### Go Transpiler Improvements (Latest)
- Fixed "declared and not used" compiler errors by analyzing variable usage
- Properly translate Python while loops to Go for loops
- Suppress unused variables with blank identifier `_`
- Selective import generation (only import used packages)

See [FIX_SUMMARY.md](FIX_SUMMARY.md) and [FIXES_APPLIED.md](FIXES_APPLIED.md) for technical details.

## Architecture Overview

```
src/
├── analyzer.py           # Feature extraction (FeatureAnalyzer, CodeFeatures)
├── comfort.py            # Segment size balancing (ComfortBalancer)
├── decision_engine.py    # Cost function (CostModel, DecisionEngine)
├── neural_classifier.py  # Neural network fallback (PolyglotClassifier, NeuralClassifier)
├── polyglot.py           # Language-specific transpilers (Rust, C++, Go, Java)
├── parser.py             # Source code parsing
├── visualizer.py         # Terminal visualization
├── html_visualizer.py    # HTML report generation
├── type_inference.py     # Type system helpers
└── strategies/           # Language-specific transpilation strategies

main.py                  # Entry point, orchestrates the pipeline
```

## Requirements

```
Python 3.9+
torch
click
(Optional) graphviz (for PDF generation)
(Optional) rustc, g++, go, java (for execution)
```

See `requirements.txt` for exact versions.

## Dependencies for Compilation

The runner script automatically detects and uses:
- **Rust**: `rustc` (https://www.rust-lang.org)
- **C++**: `g++` or MSVC (https://gcc.gnu.org)
- **Go**: `go` (https://golang.org)
- **Java**: `java` + `javac` (https://www.oracle.com/java/)

If a compiler is not found, that segment's execution is gracefully skipped.

## Future Enhancements

1. **Granular segmentation strategies**: Split by functions, control flow blocks, or loop nests
2. **Cost function learning**: Train weights from actual benchmark data
3. **Multi-pass optimization**: Profile execution, rerun transpilation with real timing data
4. **Language-specific libraries**: Recognize domain-specific patterns (e.g., numpy → Rust nalgebra)
5. **Parallelization detection**: Identify embarrassingly parallel sections for Go/Rust async
6. **Custom cost models**: Allow users to provide domain-specific weights
