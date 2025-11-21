import os

class HtmlVisualizer:
    def __init__(self, output_dir="viz"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def generate_report(self, results):
        """
        Generates a self-contained HTML report with a Mermaid diagram and code blocks.
        """
        html_path = os.path.join(self.output_dir, "polyglot_report.html")
        
        mermaid_graph = "graph TD\n"
        mermaid_graph += "    Start[Python Source] --> Split{Analysis}\n"
        
        cards = ""
        
        for i, res in enumerate(results):
            lang = res['lang']
            color = self._get_color(lang)
            node_id = f"Seg{i}"
            
            # Mermaid node
            mermaid_graph += f"    Split --> {node_id}[Segment {i}: {lang}]\n"
            mermaid_graph += f"    style {node_id} fill:{color},stroke:#333,stroke-width:2px\n"
            
            # HTML Card
            code_block = res['transpiled'].replace("<", "&lt;").replace(">", "&gt;")
            lang_class = self._get_lang_class(lang)
            
            cards += f"""
            <div class="card">
                <div class="card-header" style="background-color: {color}">
                    <span>Segment {i}: {lang}</span>
                    <span>Score: {res['score']:.1f}</span>
                </div>
                <div class="card-body">
                    <div class="meta">
                        <strong>Reasoning:</strong> {res['source']}
                    </div>
                    <pre><code class="language-{lang_class}">{code_block}</code></pre>
                </div>
            </div>
            """

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Polyglot Transpiler Report</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script>
        mermaid.initialize({{startOnLoad:true}});
        hljs.highlightAll();
    </script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; padding: 40px; color: #333; }}
        h1 {{ text-align: center; color: #2c3e50; margin-bottom: 40px; }}
        .container {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 30px; }}
        .diagram {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 40px; text-align: center; }}
        .card {{ 
            background: white; 
            padding: 0; 
            border-radius: 12px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.1); 
            width: 45%; 
            min-width: 400px; 
            overflow: hidden;
            transition: transform 0.2s;
        }}
        .card:hover {{ transform: translateY(-5px); }}
        .card-header {{ padding: 15px 20px; color: white; font-weight: bold; font-size: 1.1em; display: flex; justify-content: space-between; }}
        .card-body {{ padding: 20px; }}
        .meta {{ font-size: 0.9em; color: #666; margin-bottom: 15px; background: #f8f9fa; padding: 10px; border-radius: 6px; }}
        pre {{ margin: 0; padding: 0; }}
        code {{ border-radius: 6px; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>Polyglot Transpilation Report</h1>
    
    <div class="diagram">
        <h2>Architecture Flow</h2>
        <div class="mermaid">
            {mermaid_graph}
        </div>
    </div>

    <div class="container">
        {cards}
    </div>
</body>
</html>
"""
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return html_path

    def _get_color(self, lang):
        return {
            "Rust": "#e43b26", # Rust Orange
            "C++": "#00599C",  # C++ Blue
            "Go": "#00ADD8",   # Go Cyan
            "Java": "#b07219"  # Java Brown
        }.get(lang, "#777")

    def _get_lang_class(self, lang):
        return {
            "Rust": "rust",
            "C++": "cpp",
            "Go": "go",
            "Java": "java"
        }.get(lang, "plaintext")
