from typing import List
from src.parser import SourceSegment

class ComfortBalancer:
    """
    Balances segment sizes to ensure they are 'comfortable' to read.
    Attempts to merge small segments and ensure no segment is too massive
    (though splitting is primarily handled by strategies).
    """
    def __init__(self, min_lines: int = 5, max_lines: int = 50):
        self.min_lines = min_lines
        self.max_lines = max_lines

    def balance(self, segments: List[SourceSegment]) -> List[SourceSegment]:
        if not segments:
            return []
            
        balanced = []
        buffer_segment = None
        
        for seg in segments:
            seg_lines = seg.end_line - seg.start_line + 1
            
            if buffer_segment:
                # Try to merge with buffer
                buffer_lines = buffer_segment.end_line - buffer_segment.start_line + 1
                if buffer_lines + seg_lines <= self.max_lines:
                    # Merge
                    merged_code = buffer_segment.code + "\n" + seg.code
                    buffer_segment = SourceSegment(
                        id=f"{buffer_segment.id}_{seg.id}",
                        code=merged_code,
                        start_line=buffer_segment.start_line,
                        end_line=seg.end_line,
                        tags=buffer_segment.tags + seg.tags + ["balanced_merge"]
                    )
                    continue
                else:
                    # Flush buffer
                    balanced.append(buffer_segment)
                    buffer_segment = None
            
            if seg_lines < self.min_lines:
                buffer_segment = seg
            else:
                balanced.append(seg)
                
        if buffer_segment:
            balanced.append(buffer_segment)
            
        return balanced
