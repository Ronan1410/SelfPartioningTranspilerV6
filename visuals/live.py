import time
import tokenize
import ast
import io
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.syntax import Syntax
from rich.live import Live
from rich.tree import Tree
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

class LiveVisualizer:
    def __init__(self):
        self.console = Console()

    def visualize_process(self, source_code: str):
        """
        Runs a live visualization of the Lexing and Parsing process.
        """
        self.console.clear()
        self.console.rule("[bold blue]SelfPartitioningTranspilerV5 Live Process")
        
        # 1. Lexer Visualization
        self._visualize_lexer(source_code)
        
        # 2. Parser Visualization
        self._visualize_parser(source_code)

    def _visualize_lexer(self, source_code: str):
        self.console.print("\n[bold green]Step 1: Lexical Analysis (Tokenization)[/bold green]")
        
        tokens = list(tokenize.tokenize(io.BytesIO(source_code.encode('utf-8')).readline))
        
        # Create a table for tokens
        table = Table(title="Token Stream", show_lines=True)
        table.add_column("Type", style="cyan", no_wrap=True)
        table.add_column("String", style="magenta")
        table.add_column("Position", style="yellow")
        
        with Live(table, refresh_per_second=10) as live:
            for token in tokens:
                if token.type == tokenize.ENCODING:
                    continue
                    
                token_type = tokenize.tok_name[token.type]
                token_str = repr(token.string)
                pos = f"{token.start[0]}:{token.start[1]}"
                
                table.add_row(token_type, token_str, pos)
                time.sleep(0.05)  # Simulate processing time

    def _visualize_parser(self, source_code: str):
        self.console.print("\n[bold green]Step 2: Parsing (AST Generation)[/bold green]")
        
        tree_root = ast.parse(source_code)
        
        # Create a Rich Tree
        rich_tree = Tree("Module")
        
        # We will walk the tree and update the visualization
        # Since ast.walk is iterative/recursive, we need a way to map it to the visual tree.
        # Let's build the visual tree recursively with delays.
        
        with Live(rich_tree, refresh_per_second=4) as live:
            self._add_node_recursive(rich_tree, tree_root)
            
    def _add_node_recursive(self, parent_tree, node):
        time.sleep(0.1) # Delay for effect
        
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        branch = parent_tree.add(f"[bold blue]{type(item).__name__}[/bold blue]")
                        self._add_node_recursive(branch, item)
            elif isinstance(value, ast.AST):
                branch = parent_tree.add(f"[bold blue]{type(value).__name__}[/bold blue]")
                self._add_node_recursive(branch, value)
            else:
                # Scalar value
                pass
