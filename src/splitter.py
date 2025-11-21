from typing import List
from src.parser import CodeParser, ParsedModule, SourceSegment
from src.strategies.base import SplitStrategy
from src.strategies.markers import MarkerStrategy
from src.strategies.heuristic import HeuristicStrategy
from src.strategies.neural import NeuralStrategy
from src.comfort import ComfortBalancer

class SplitterOrchestrator:
    def __init__(self):
        self.strategies: List[SplitStrategy] = [
            MarkerStrategy(),
            HeuristicStrategy(),
            NeuralStrategy()
        ]
        self.comfort = ComfortBalancer()

    def process_module(self, parsed_module: ParsedModule) -> ParsedModule:
        current_segments = parsed_module.segments
        
        # 1. Apply Strategies sequentially
        for strategy in self.strategies:
            new_segments = []
            for seg in current_segments:
                # Apply strategy to each segment
                result = strategy.apply(seg)
                new_segments.extend(result)
            current_segments = new_segments
            
        # 2. Apply Comfort Function
        final_segments = self.comfort.balance(current_segments)
        
        parsed_module.segments = final_segments
        return parsed_module
