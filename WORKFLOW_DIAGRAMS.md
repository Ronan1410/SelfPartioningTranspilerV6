# SelfPartioningTranspiler V6 - Workflow Diagrams

## Complete System Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                  SelfPartioningTranspiler V6                      │
│                   Complete System Architecture                     │
└───────────────────────────────────────────────────────────────────┘

┌──────────────┐
│ Python Code  │
└──────┬───────┘
       │
       ▼
┌────────────────────────────────────────────────────────┐
│          Entry Point Selection                         │
├────────────────────────────────────────────────────────┤
│  • interactive_cli.py      (Interactive Menu)         │
│  • main_enhanced.py        (CLI with Options)          │
│  • main.py                 (Original)                  │
└────────┬──────────────────────────────────────┬────────┘
         │                                      │
    ┌────▼────┐                         ┌──────▼────┐
    │ AST     │                         │ Feature  │
    │ Parser  │                         │Extraction│
    └────┬────┘                         └──────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│              Code Segmentation                         │
├────────────────────────────────────────────────────────┤
│ Splits code by:                                        │
│  • Functions (FunctionDef)                            │
│  • Classes (ClassDef)                                 │
│  • Async Functions (AsyncFunctionDef)                 │
│  • Top-level statements                              │
└────┬──────────────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────────────┐
│          Feature Analysis & Data Flow                  │
├────────────────────────────────────────────────────────┤
│ FeatureAnalyzer:           DataBridgeAnalyzer:         │
│  • Math operations          • Input variables          │
│  • I/O operations           • Output variables         │
│  • Loops                    • Variable types           │
│  • Classes                  • Dependencies             │
│  • Async operations                                    │
└────┬──────────────────────┬──────────────────────────┘
     │                      │
     ▼                      ▼
┌─────────────────┐  ┌─────────────────┐
│ CodeFeatures    │  │ SegmentInterface│
│  - counts       │  │  - inputs       │
│  - patterns     │  │  - outputs      │
│  - complexity   │  │  - types        │
└────────┬────────┘  └────────┬────────┘
         │                    │
         └────────┬───────────┘
                  │
                  ▼
     ┌────────────────────────────────┐
     │  Decision Engine               │
     ├────────────────────────────────┤
     │  Cost Function:                │
     │   • Rust:  math=1.0, io=0.8    │
     │   • C++:   math=1.0, io=0.9    │
     │   • Go:    io=1.0, async=1.0   │
     │   • Java:  classes=2.0         │
     │                                │
     │  score = Σ(features × weights) │
     │                                │
     │  margin = top_score - 2nd      │
     │  if margin < 0.1:              │
     │    → Use Neural Network        │
     └────────┬──────────────────────┘
              │
              ├─────────────┬──────────────┬──────────────┐
              ▼             ▼              ▼              ▼
         ┌────────┐   ┌────────┐    ┌────────┐    ┌────────┐
         │ Rust   │   │ C++    │    │  Go    │    │ Java   │
         │Score   │   │ Score  │    │ Score  │    │ Score  │
         └────┬───┘   └───┬────┘    └───┬────┘    └───┬────┘
              │           │            │           │
              └───────────┴────────────┴───────────┘
                          │
              ┌───────────▼─────────────┐
              │ Select Best Language    │
              │ (Highest Score)         │
              └───────────┬─────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│          Language-Specific Transpilers                 │
├────────────────────────────────────────────────────────┤
│ RustTranspiler    • Type annotations, ownership       │
│ CppTranspiler     • Headers, namespaces              │
│ GoTranspiler      • Package structure, simplicity    │
│ JavaTranspiler    • Classes, OOP patterns            │
└────┬───────────────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────────────────────┐
│          Generated Code (4 Languages)                  │
├────────────────────────────────────────────────────────┤
│ segment_0_Rust.rs      segment_2_Go.go                 │
│ segment_1_Cpp.cpp      segment_3_Java.java             │
└────┬──────────────────────────────────────────────────┘
     │
     ├─────────────────┬──────────────────┬─────────────┐
     │                 │                  │             │
     ▼                 ▼                  ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌────────────┐ ┌──────────────┐
│ Compiler:    │ │ Compiler:    │ │ Compiler:  │ │ Not compiled │
│ rustc        │ │ g++          │ │ go (build) │ │ (interpreted)│
└──────┬───────┘ └──────┬───────┘ └──────┬─────┘ └──────┬───────┘
       │                │                │             │
       └────────────────┴────────────────┴─────────────┘
                        │
         ┌──────────────▼──────────────┐
         │ Benchmarker                 │
         ├─────────────────────────────┤
         │ Measures:                   │
         │  • Execution Time           │
         │  • Memory Usage (peak)      │
         │  • Exit Code                │
         │  • stdout/stderr            │
         └──────────┬──────────────────┘
                    │
                    ▼
         ┌──────────────────────────┐
         │ ComparisonMetrics        │
         ├──────────────────────────┤
         │  • Speedup (Python/Trans)│
         │  • Memory Reduction %    │
         │  • Efficiency Score (0-1)│
         └──────────┬───────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────────────┐
│         Metrics Visualization                          │
├────────────────────────────────────────────────────────┤
│ MetricsVisualizer generates:                           │
│  • Summary Cards (Speedup, Memory, Efficiency)        │
│  • Execution Time Chart                               │
│  • Memory Usage Chart                                 │
│  • Speedup Factor Chart                               │
│  • Detailed Breakdown Table                           │
│  • Efficiency Gauge                                   │
│  • Data Flow Visualization                            │
└────┬────────────────────────────────────────────────┬─┘
     │                                                │
     ▼                                                ▼
┌──────────────────────────────┐  ┌──────────────────────────┐
│ viz/metrics_report.html      │  │ out_dir/analysis_report  │
│  (Interactive HTML)          │  │ .json (Metadata)         │
│  • Beautiful Charts          │  │  • Segments list         │
│  • Responsive Design         │  │  • Language choices      │
│  • Hover Effects             │  │  • Metrics values        │
│  • Professional Styling      │  │  • Execution order       │
└──────────────────────────────┘  └──────────────────────────┘
```

---

## Interactive CLI Workflow

```
┌─────────────────────────────────────────────────────┐
│         Start: python interactive_cli.py            │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
       ┌───────────────────┐
       │   Main Menu       │
       ├───────────────────┤
       │ 1. Input Code     │
       │ 2. Load File      │
       │ 3. Analyze        │
       │ 4. Benchmark      │
       │ 5. View Metrics   │
       │ 6. Save Results   │
       │ 7. View Code      │
       │ 8. Exit           │
       └────────┬──────────┘
                │
     ┌──────────┼──────────────────────────────────┐
     │          │                                  │
     ▼          ▼                                  │
  ┌──────┐  ┌────────┐                            │
  │Input │  │ Load   │                            │
  │Code  │  │ File   │                            │
  └──┬───┘  └───┬────┘                            │
     │          │                                  │
     │    ┌─────┴──────┐                          │
     │    │            │                          │
     │    ▼            ▼                          │
     │  ┌──────────────────────────────┐          │
     │  │  Source Code Ready           │          │
     │  └──────────┬───────────────────┘          │
     │             │                              │
     └─────────────┼──────────────────────────────┘
                   │
                   ▼
         ┌──────────────────────┐
         │ Analyze & Transpile  │
         ├──────────────────────┤
         │ 1. Parse code        │
         │ 2. Extract segments  │
         │ 3. Analyze features  │
         │ 4. Analyze data flow │
         │ 5. Decide languages  │
         │ 6. Transpile         │
         │ 7. Save files        │
         └──────┬───────────────┘
                │
                ▼
         ┌──────────────────────┐
         │ Results Ready        │
         │ (4 transpiled files) │
         └──────┬───────────────┘
                │
        ┌───────┴───────┐
        │               │
        ▼               ▼
  ┌──────────┐   ┌──────────────┐
  │Benchmark │   │View Code     │
  │(Optional)│   │Comparison    │
  └────┬─────┘   └──────┬───────┘
       │                │
       └────────┬───────┘
                │
                ▼
         ┌──────────────────┐
         │View Metrics &    │
         │Results (HTML)    │
         └──────┬───────────┘
                │
                ▼
         ┌──────────────────┐
         │Save All Results  │
         │to out_dir/       │
         └──────┬───────────┘
                │
                ▼
         ┌──────────────────┐
         │Return to Menu    │
         │or Exit           │
         └──────────────────┘
```

---

## Feature Analysis Flow

```
┌────────────────────────────────┐
│   Python Code (AST)            │
└────────────┬───────────────────┘
             │
             ▼
    ┌────────────────────┐
    │ FeatureAnalyzer    │
    │ (AST Visitor)      │
    └────────┬───────────┘
             │
        ┌────┼─────────────────────────────────────┐
        │    │                                     │
        ▼    ▼                                     │
    ┌──────────────┐                             │
    │ visit_BinOp  │ → math_ops++                │
    └──────────────┘                             │
        ┌──────────────┐                         │
        │ visit_Call   │ → Check if print/open   │
        │              │    io_ops++             │
        │              │ → else functions++      │
        └──────────────┘                         │
        ┌──────────────┐                         │
        │ visit_For    │ → loops++               │
        │ visit_While  │                         │
        └──────────────┘                         │
        ┌──────────────┐                         │
        │ visit_If     │ → conditionals++        │
        └──────────────┘                         │
        ┌──────────────┐                         │
        │visit_ClassDef│ → classes++             │
        └──────────────┘                         │
        ┌──────────────────┐                     │
        │visit_AsyncFunc   │ → async_ops++       │
        │visit_Await       │                     │
        └──────────────────┘                     │
        ┌──────────────┐                         │
        │visit_Constant│ → if str: string_ops++  │
        └──────────────┘                         │
                │                                │
                └───────────────────────────────┘
                           │
                           ▼
           ┌────────────────────────────────┐
           │  CodeFeatures                  │
           ├────────────────────────────────┤
           │ math_ops:     5                │
           │ io_ops:       2                │
           │ loops:        3                │
           │ conditionals: 2                │
           │ functions:    4                │
           │ classes:      1                │
           │ async_ops:    0                │
           │ recursion:    true             │
           │ string_ops:   8                │
           └────────────────────────────────┘
```

---

## Cost Function Decision Flow

```
┌──────────────────────────────┐
│   CodeFeatures (9 values)    │
└────────────┬─────────────────┘
             │
             ▼
    ┌────────────────────────────────────────┐
    │  For each language (Rust, C++, Go, Java)
    └────────┬─────────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────────┐
    │  Calculate Score:                      │
    │  score = base_cost * 10.0              │
    │        + math_ops * weight_math * 2.0  │
    │        + io_ops * weight_io * 2.0      │
    │        + loops * weight_loops * 3.0    │
    │        + strings * weight_strings*1.5  │
    │        + classes * weight_classes*10.0 │
    │        + async * weight_async * 5.0    │
    │        + (recursion ? weight_rec*15 :0)│
    └────────┬─────────────────────────────┘
             │
             ▼
    ┌─────────────────────────────┐
    │ Scores Dict:                │
    │  Rust:  16.5                │
    │  C++:   15.8                │
    │  Go:    13.2                │
    │  Java:  12.0                │
    └────────┬────────────────────┘
             │
             ▼
    ┌─────────────────────────────┐
    │ Find Max Score: Rust (16.5) │
    └────────┬────────────────────┘
             │
             ▼
    ┌─────────────────────────────┐
    │ Calculate Margin:           │
    │ margin = 16.5 - 15.8 = 0.7  │
    └────────┬────────────────────┘
             │
       ┌─────┴─────┐
       │           │
    margin >= 0.1  margin < 0.1
       │           │
       ▼           ▼
   ┌────────┐  ┌─────────────────┐
   │ Rust   │  │ Neural Network  │
   │Selected│  │ Fallback        │
   └────────┘  │ (inconclusive)  │
               └─────────────────┘
```

---

## Data Flow Analysis

```
┌────────────────────────────────────┐
│  Segment 0:                        │
│  def fibonacci(n):                 │
│      if n <= 1:                    │
│          return n                  │
│      return fib(n-1) + fib(n-2)   │
└────────┬───────────────────────────┘
         │
         ▼
    ┌──────────────────────────┐
    │ DataBridgeAnalyzer       │
    │  • Scan assignments      │
    │  • Scan usages           │
    │  • Classify variables    │
    └────────┬─────────────────┘
             │
             ▼
    ┌──────────────────────────┐
    │ SegmentInterface:        │
    │ Inputs:                  │
    │   n: int (param)         │
    │                          │
    │ Outputs:                 │
    │   return: int            │
    │                          │
    │ Internal:                │
    │   none                   │
    └──────────────────────────┘
              │
              ▼
    ┌──────────────────────────┐
    │ Segment 1:               │
    │ def process(result):     │
    │     total = 0            │
    │     for r in result:     │
    │         total += r       │
    │     return total         │
    └────────┬─────────────────┘
             │
             ▼
    ┌──────────────────────────┐
    │ SegmentInterface:        │
    │ Inputs:                  │
    │   result: list           │
    │                          │
    │ Outputs:                 │
    │   total: int             │
    │                          │
    │ Internal:                │
    │   r: int (loop var)      │
    └──────────────────────────┘
              │
              ▼
    ┌───────────────────────────────────┐
    │ Dependency Analysis:              │
    │ • Segment 0 output (return)       │
    │   matches Segment 1 input (result)│
    │ • Execution order: [0, 1]         │
    │                                   │
    │ Connectors needed:                │
    │ • After Seg 0: export return val  │
    │ • Before Seg 1: import return val │
    └───────────────────────────────────┘
```

---

## Benchmarking Process

```
┌──────────────────────────┐
│  Python Code             │
└────────┬─────────────────┘
         │
         ▼
    ┌─────────────────────────────────┐
    │ Create temp Python file         │
    │ Start timing (time.time())       │
    │ Monitor memory (psutil)          │
    │ Execute via subprocess          │
    │ Capture stdout/stderr           │
    │ Record peak memory              │
    │ Stop timing                     │
    └────────┬────────────────────────┘
             │
             ▼
    ┌──────────────────────────┐
    │ BenchmarkResult:         │
    │  execution_time: 0.052s  │
    │  memory_used: 2.15 MB    │
    │  peak_memory: 2.15 MB    │
    │  exit_code: 0            │
    │  output: "..."           │
    └──────────────────────────┘
         │
         ├─────────────────────────┐
         │                         │
         ▼                         ▼
┌──────────────────┐    ┌──────────────────┐
│ Transpiled Code  │    │ Transpiled Code  │
│ (Rust)           │    │ (C++)            │
├──────────────────┤    ├──────────────────┤
│ Compile:         │    │ Compile:         │
│ rustc -O         │    │ g++ -O2          │
│ Run & Monitor:   │    │ Run & Monitor:   │
│ time: 0.001s     │    │ time: 0.002s     │
│ mem: 0.48 MB     │    │ mem: 0.52 MB     │
└──────────┬───────┘    └────────┬─────────┘
           │                    │
           └──────────┬─────────┘
                      │
                      ▼
    ┌─────────────────────────────────┐
    │ ComparisonMetrics:              │
    │  Python time:      0.052s       │
    │  Transpiled time:  0.0025s avg  │
    │  Speedup:          20.8x        │
    │  Python mem:       2.15 MB      │
    │  Transpiled mem:   0.50 MB      │
    │  Memory reduction: 76.7%        │
    │  Efficiency score: 89/100       │
    └─────────────────────────────────┘
```

---

## Metrics Visualization Pipeline

```
┌──────────────────────────────┐
│  ComparisonMetrics (dict)    │
├──────────────────────────────┤
│ {                            │
│   0: ComparisonMetrics(...), │
│   1: ComparisonMetrics(...), │
│   2: ComparisonMetrics(...), │
│   3: ComparisonMetrics(...)  │
│ }                            │
└────────┬─────────────────────┘
         │
         ▼
    ┌──────────────────────────────────────┐
    │  MetricsVisualizer                   │
    │  .generate_comparison_html()         │
    └────────┬─────────────────────────────┘
             │
             ├─────────────────┬──────────────┐
             │                 │              │
             ▼                 ▼              ▼
    ┌──────────────┐  ┌────────────────┐ ┌────────────────┐
    │HTML Header   │  │CSS Styling     │ │JavaScript      │
    │DOCTYPE       │  │Grid Layout     │ │Chart.js config │
    │Meta tags     │  │Colors/Gradients│ │Event handlers  │
    └──────────────┘  └────────────────┘ └────────────────┘
             │                 │              │
             └──────────────────┴──────────────┘
                      │
                      ▼
    ┌────────────────────────────────────────┐
    │  Summary Section                       │
    ├────────────────────────────────────────┤
    │  Cards:                                │
    │   • Overall Speedup: 25.7x             │
    │   • Memory Reduction: 78.1%            │
    │   • Average Efficiency: 92/100         │
    └────────────────────────────────────────┘
                      │
                      ▼
    ┌────────────────────────────────────────┐
    │  Performance Charts                    │
    ├────────────────────────────────────────┤
    │   • Execution Time (Bar chart)         │
    │   • Memory Usage (Bar chart)           │
    │   • Speedup Factor (Bar chart)         │
    └────────────────────────────────────────┘
                      │
                      ▼
    ┌────────────────────────────────────────┐
    │  Detailed Breakdown Table              │
    ├────────────────────────────────────────┤
    │ Seg │Python│Transpiled│Speedup│Efficiency
    │  0  │52.3ms│1.2ms     │43.58x │95/100
    │  1  │12.1ms│1.8ms     │6.72x  │78/100
    └────────────────────────────────────────┘
                      │
                      ▼
    ┌────────────────────────────────────────┐
    │  Efficiency Gauge                      │
    ├────────────────────────────────────────┤
    │  Circular indicator: 92/100            │
    │  Color: Green (Excellent)              │
    │  Formula display                       │
    └────────────────────────────────────────┘
                      │
                      ▼
    ┌────────────────────────────────────────┐
    │  Data Flow Visualization               │
    ├────────────────────────────────────────┤
    │  Segment dependencies & inputs/outputs │
    └────────────────────────────────────────┘
                      │
                      ▼
    ┌────────────────────────────────────────┐
    │  HTML Footer                           │
    ├────────────────────────────────────────┤
    │  Copyright & Project Info              │
    └────────────────────────────────────────┘
                      │
                      ▼
         ┌─────────────────────────┐
         │ viz/metrics_report.html │
         │ (1000+ lines, 50+KB)    │
         │ Interactive, Beautiful  │
         │ Charts & Tables         │
         └─────────────────────────┘
```

---

## Command Execution Flow

```
┌──────────────────────────────────┐
│  User Command                    │
├──────────────────────────────────┤
│  python main_enhanced.py file.py │
│  --benchmark --show-metrics      │
└────────┬─────────────────────────┘
         │
         ▼
    ┌──────────────────────────┐
    │ Parse Arguments           │
    │ input_file: file.py      │
    │ benchmark: True          │
    │ show_metrics: True       │
    └────────┬─────────────────┘
             │
             ▼
    ┌──────────────────────────────────┐
    │ STEP 1: Parsing & Segmentation   │
    │ status: 70% [████░░░░░]          │
    └────────┬─────────────────────────┘
             │
             ▼
    ┌──────────────────────────────────┐
    │ STEP 2: Feature Analysis         │
    │ status: 40% [██░░░░░░░]          │
    └────────┬─────────────────────────┘
             │
             ▼
    ┌──────────────────────────────────┐
    │ STEP 3: Code Generation          │
    │ status: 100% [██████████]        │
    └────────┬─────────────────────────┘
             │
             ▼
    ┌──────────────────────────────────┐
    │ STEP 4: Benchmarking (if flag)   │
    │ Python... Done!                  │
    │ Rust... Done!                    │
    │ C++... Done!                     │
    │ status: 50% [█████░░░░░]         │
    └────────┬─────────────────────────┘
             │
             ▼
    ┌──────────────────────────────────┐
    │ STEP 5: Visualization            │
    │ HTML Report... Done!             │
    │ Metrics Report... Done!          │
    │ status: 100% [██████████]        │
    └────────┬─────────────────────────┘
             │
             ▼
    ┌──────────────────────────────────┐
    │ STEP 6: Data Flow Analysis       │
    │ Dependency analysis... Done!     │
    │ Execution order: [0, 1, 2, 3]   │
    └────────┬─────────────────────────┘
             │
             ▼
    ┌──────────────────────────────────┐
    │ ✅ ANALYSIS COMPLETE             │
    │                                  │
    │ Output directory: out_dir/       │
    │ • segment_0_Rust.rs            │
    │ • segment_1_Cpp.cpp            │
    │ • segment_2_Go.go              │
    │ • segment_3_Java.java          │
    │ • runner.py                    │
    │                                  │
    │ Visualization: viz/              │
    │ • metrics_report.html          │
    │ • report.html                  │
    └──────────────────────────────────┘
```

---

These diagrams illustrate the complete architecture, workflows, and data flow of SelfPartioningTranspiler V6.
