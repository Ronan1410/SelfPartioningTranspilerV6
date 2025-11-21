import os
from graphviz import Digraph
from graphviz.backend.execute import ExecutableNotFound
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout

class Visualizer:
    def __init__(self, output_dir="viz"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        self.console = Console()

    def generate_flow_graph(self, segments_data):
        """
        Generates a DOT graph showing the flow between language segments.
        """
        dot = Digraph(comment='Polyglot Flow')
        dot.attr(rankdir='TB')
        
        lang_colors = {
            "Rust": "orange",
            "C++": "lightblue",
            "Go": "cyan",
            "Java": "lightgrey"
        }

        for i, seg in enumerate(segments_data):
            lang = seg['lang']
            color = lang_colors.get(lang, "white")
            
            label = f"Segment {i}\nLanguage: {lang}\nScore: {seg['score']:.2f}"
            dot.node(str(i), label, shape='box', style='filled', fillcolor=color)
            
            if i > 0:
                dot.edge(str(i-1), str(i))

        output_path = os.path.join(self.output_dir, "polyglot_flow.gv")
        try:
            dot.render(output_path, view=False)
        except ExecutableNotFound:
            # Graphviz 'dot' binary not found on PATH — save DOT source instead
            self.console.print("[yellow]Graphviz 'dot' executable not found; saving DOT file instead.[/yellow]")
            dot.save(output_path)
        except Exception as e:
            # Unexpected error while rendering — still try to save DOT source
            self.console.print(f"[red]Failed to render graph: {e}. Saved DOT file instead.[/red]")
            dot.save(output_path)

        return output_path

    def print_summary(self, segments_data):
        """
        Prints a rich table summary to the terminal.
        """
        table = Table(title="Polyglot Transpilation Results")
        
        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Target Language", style="magenta")
        table.add_column("Reasoning (Top Factor)", style="green")
        table.add_column("Confidence", style="yellow")
        
        for i, seg in enumerate(segments_data):
            # Determine top factor simple heuristic for display
            f = seg['features']
            reason = "General"
            if f.math_ops > 2: reason = "Math Intensity"
            elif f.io_ops > 2: reason = "IO Operations"
            elif f.loops > 0: reason = "Loop Performance"
            elif f.classes > 0: reason = "OOP Structure"
            elif f.async_ops > 0: reason = "Concurrency"
            
            table.add_row(str(i), seg['lang'], reason, f"{seg['score']:.2f}")
            
        self.console.print(table)
