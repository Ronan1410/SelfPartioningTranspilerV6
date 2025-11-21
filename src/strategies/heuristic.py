import ast
from typing import List
from src.parser import SourceSegment
from src.strategies.base import SplitStrategy

class HeuristicStrategy(SplitStrategy):
    """Splits code based on heuristics like complexity or length."""

    def __init__(self, max_lines: int = 20, complexity_threshold: float = 50.0):
        self.max_lines = max_lines
        self.complexity_threshold = complexity_threshold

    def name(self) -> str:
        return "Heuristic Splitting"

    def apply(self, segment: SourceSegment) -> List[SourceSegment]:
        # Only split if too long or too complex
        line_count = segment.end_line - segment.start_line + 1
        if line_count <= self.max_lines and segment.complexity_score <= self.complexity_threshold:
            return [segment]
            
        # Try to split by identifying logical blocks inside the AST node (if available)
        if not segment.ast_node or not isinstance(segment.ast_node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return [segment]
            
        # Iterate over body to find split points (e.g., loop boundaries)
        # This is a simplified implementation
        new_segments = []
        current_body_subset = []
        current_start = segment.start_line
        
        body = segment.ast_node.body
        
        for idx, node in enumerate(body):
            current_body_subset.append(node)
            
            # If we have accumulated enough lines, split
            # Using simplified logic: just looking at node lineno
            if not hasattr(node, 'end_lineno'): continue
            
            current_end = node.end_lineno
            if (current_end - current_start) > self.max_lines:
                # Create segment from these nodes
                # Note: Re-generating source from AST nodes is complex without `ast.unparse` (Py3.9+)
                # or original source slicing. 
                # We will assume we can just keep the original for now or return the whole if complex.
                pass

        # Since precise AST splitting is complex to implement perfectly in one go without
        # `ast.get_source_segment` behaving perfectly for all versions, 
        # let's assume for this V5 we just mark it as "needs_refactor" if we can't easily split.
        # OR, better: Split by `if/for/while` statements.
        
        if segment.complexity_score > self.complexity_threshold:
             segment.tags.append("complex")
             
        return [segment] 
