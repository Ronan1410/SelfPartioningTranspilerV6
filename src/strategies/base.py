from abc import ABC, abstractmethod
from typing import List
from src.parser import SourceSegment

class SplitStrategy(ABC):
    """Abstract base class for splitting strategies."""
    
    @abstractmethod
    def name(self) -> str:
        pass
        
    @abstractmethod
    def apply(self, segment: SourceSegment) -> List[SourceSegment]:
        """
        Analyzes the segment and potentially splits it into smaller segments.
        Returns a list of segments (original if no split).
        """
        pass
