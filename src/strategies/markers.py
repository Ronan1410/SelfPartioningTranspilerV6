import ast
from typing import List
from src.parser import SourceSegment
from src.strategies.base import SplitStrategy

class MarkerStrategy(SplitStrategy):
    """Splits code based on explicit '# SPLIT' markers."""

    def name(self) -> str:
        return "Marker-based Splitting"

    def apply(self, segment: SourceSegment) -> List[SourceSegment]:
        if "# SPLIT" not in segment.code:
            return [segment]
            
        # Naive splitting by line for demo purposes
        # In production, we would carefully reconstruct AST or preserve indentation
        lines = segment.code.splitlines()
        new_segments = []
        current_chunk = []
        start_line = segment.start_line
        
        for i, line in enumerate(lines):
            if "# SPLIT" in line:
                if current_chunk:
                    code_str = "\n".join(current_chunk)
                    new_segments.append(SourceSegment(
                        id=f"{segment.id}_p{len(new_segments)}",
                        code=code_str,
                        start_line=start_line,
                        end_line=start_line + len(current_chunk) - 1,
                        tags=["explicit_split"]
                    ))
                    current_chunk = []
                start_line = segment.start_line + i + 1
            else:
                current_chunk.append(line)
                
        if current_chunk:
            code_str = "\n".join(current_chunk)
            new_segments.append(SourceSegment(
                id=f"{segment.id}_p{len(new_segments)}",
                code=code_str,
                start_line=start_line,
                end_line=segment.end_line,
                tags=["remainder"]
            ))
            
        return new_segments
