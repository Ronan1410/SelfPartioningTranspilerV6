import os
from src.parser import ParsedModule

class ReportGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    def generate(self, module: ParsedModule):
        report_path = os.path.join(self.output_dir, f"report_{os.path.basename(module.path)}.md")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# Analysis Report for {module.path}\n\n")
            f.write(f"Total Segments: {len(module.segments)}\n\n")
            
            f.write("## Segments Details\n\n")
            for seg in module.segments:
                f.write(f"### Segment: {seg.id}\n")
                f.write(f"- **Lines**: {seg.start_line} to {seg.end_line}\n")
                f.write(f"- **Tags**: {', '.join(seg.tags) if seg.tags else 'None'}\n")
                f.write(f"- **Complexity**: {seg.complexity_score}\n")
                f.write("```python\n")
                f.write(seg.code)
                f.write("\n```\n\n")
        
        print(f"Report generated at {report_path}")
