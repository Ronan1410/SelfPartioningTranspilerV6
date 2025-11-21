import os
import json
import dataclasses
from src.parser import ParsedModule

class MetadataGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    def generate(self, module: ParsedModule):
        # Need a custom encoder for AST nodes (skip them)
        def default(o):
            if hasattr(o, '__dict__'):
                d = o.__dict__.copy()
                if 'ast_node' in d:
                    del d['ast_node']
                return d
            return str(o)

        output_path = os.path.join(self.output_dir, f"metadata_{os.path.basename(module.path)}.json")
        
        data = dataclasses.asdict(module)
        # Remove non-serializable parts manually or use the encoder above
        # dataclasses.asdict is recursive, so we need to handle ast_node inside segments
        
        # Let's just build a clean dict
        clean_segments = []
        for seg in module.segments:
            clean_segments.append({
                "id": seg.id,
                "code": seg.code,
                "start_line": seg.start_line,
                "end_line": seg.end_line,
                "tags": seg.tags,
                "complexity_score": seg.complexity_score
            })
            
        clean_data = {
            "path": module.path,
            "segments": clean_segments
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(clean_data, f, indent=2)
            
        print(f"Metadata generated at {output_path}")
