import ast
import inspect
from dataclasses import dataclass, field
from typing import List, Optional, Any

@dataclass
class SourceSegment:
    """Represents a contiguous segment of code."""
    id: str
    code: str
    start_line: int
    end_line: int
    ast_node: Optional[ast.AST] = None
    tags: List[str] = field(default_factory=list)
    complexity_score: float = 0.0

@dataclass
class ParsedModule:
    """Represents the parsed source file structure."""
    path: str
    source: str
    segments: List[SourceSegment] = field(default_factory=list)

class CodeParser:
    def __init__(self):
        pass

    def parse_file(self, file_path: str) -> ParsedModule:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        return self.parse_source(source, file_path)

    def parse_source(self, source: str, file_path: str = "<string>") -> ParsedModule:
        tree = ast.parse(source)
        segments = []
        
        # We want to identify split candidates. 
        # For this V5, we treat every top-level function/class as a primary block,
        # and then we might split INSIDE those blocks if they are large.
        # Or we treat top-level statements as the atomic units.
        
        # Let's go with a granular approach: Extract statements.
        # But to keep context, let's iterate top-level nodes.
        
        lines = source.splitlines()
        
        for i, node in enumerate(tree.body):
            # Get source lines for this node
            # ast.get_source_segment is available in Python 3.8+
            segment_code = ast.get_source_segment(source, node)
            if not segment_code:
                continue
                
            start_line = node.lineno
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
            
            seg = SourceSegment(
                id=f"seg_{i}",
                code=segment_code,
                start_line=start_line,
                end_line=end_line,
                ast_node=node
            )
            
            # Calculate basic complexity
            seg.complexity_score = self._calculate_complexity(node)
            segments.append(seg)
            
        return ParsedModule(path=file_path, source=source, segments=segments)

    def _calculate_complexity(self, node: ast.AST) -> float:
        # Simple heuristic: count nodes in the subtree
        count = 0
        for _ in ast.walk(node):
            count += 1
        return float(count)
