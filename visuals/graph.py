import os
from graphviz import Digraph
from typing import List
from src.parser import SourceSegment, ParsedModule

class GraphGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    def generate(self, module: ParsedModule):
        dot = Digraph(comment=f'Visualization for {module.path}')
        dot.attr(rankdir='TB')
        
        for i, seg in enumerate(module.segments):
            color = "lightgrey"
            if "neural_split" in seg.tags:
                color = "lightblue"
            elif "explicit_split" in seg.tags:
                color = "lightgreen"
            elif "balanced_merge" in seg.tags:
                color = "lightyellow"
            elif "complex" in seg.tags:
                color = "salmon"
                
            label = f"ID: {seg.id}\nLines: {seg.start_line}-{seg.end_line}\nTags: {seg.tags}"
            dot.node(seg.id, label, shape='box', style='filled', fillcolor=color)
            
            if i > 0:
                dot.edge(module.segments[i-1].id, seg.id)
                
        output_path = os.path.join(self.output_dir, f"graph_{os.path.basename(module.path)}.gv")
        dot.render(output_path, view=False)
        print(f"Graph generated at {output_path}.pdf")
