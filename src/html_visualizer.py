import os
import tokenize
import ast
import io

class HtmlVisualizer:
    def __init__(self, output_dir="viz"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def generate_report(self, results):
        """
        Generates a self-contained HTML report with Mermaid diagram, code blocks, and AST/Lexer visuals.
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
            
            # Generate Lexer/Parser visuals
            lexer_viz = self._visualize_lexer(res['original'])
            parser_viz = self._visualize_parser(res['original'])
            
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
                    
                    <div class="tabs">
                        <button class="tab-btn active" onclick="openTab(event, 'code{i}')">Transpiled Code</button>
                        <button class="tab-btn" onclick="openTab(event, 'lexer{i}')">Lexer (Tokens)</button>
                        <button class="tab-btn" onclick="openTab(event, 'parser{i}')">Parser (AST)</button>
                    </div>

                    <div id="code{i}" class="tab-content" style="display:block">
                        <pre><code class="language-{lang_class}">{code_block}</code></pre>
                    </div>
                    
                    <div id="lexer{i}" class="tab-content">
                        <div class="token-stream">
                            {lexer_viz}
                        </div>
                    </div>
                    
                    <div id="parser{i}" class="tab-content">
                        <pre><code class="language-python">{parser_viz}</code></pre>
                    </div>
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
        
        function openTab(evt, tabName) {{
            var i, tabcontent, tablinks;
            // Find the parent card of the clicked button
            var card = evt.currentTarget.closest('.card');
            
            // Hide all tab content in this card
            tabcontent = card.getElementsByClassName("tab-content");
            for (i = 0; i < tabcontent.length; i++) {{
                tabcontent[i].style.display = "none";
            }}
            
            // Remove active class from all buttons in this card
            tablinks = card.getElementsByClassName("tab-btn");
            for (i = 0; i < tablinks.length; i++) {{
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }}
            
            // Show the specific tab content and active button
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }}
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
            min-width: 500px; 
            overflow: hidden;
            transition: transform 0.2s;
        }}
        .card-header {{ padding: 15px 20px; color: white; font-weight: bold; font-size: 1.1em; display: flex; justify-content: space-between; }}
        .card-body {{ padding: 20px; }}
        .meta {{ font-size: 0.9em; color: #666; margin-bottom: 15px; background: #f8f9fa; padding: 10px; border-radius: 6px; }}
        pre {{ margin: 0; padding: 0; }}
        code {{ border-radius: 6px; font-size: 0.9em; max-height: 400px; overflow-y: auto; }}
        
        /* Tabs */
        .tabs {{ overflow: hidden; border-bottom: 1px solid #ccc; margin-bottom: 10px; }}
        .tab-btn {{ background-color: inherit; float: left; border: none; outline: none; cursor: pointer; padding: 10px 16px; transition: 0.3s; font-weight: 600; color: #555; }}
        .tab-btn:hover {{ background-color: #ddd; }}
        .tab-btn.active {{ border-bottom: 2px solid #333; color: #333; }}
        .tab-content {{ display: none; animation: fadeEffect 0.5s; }}
        @keyframes fadeEffect {{ from {{opacity: 0;}} to {{opacity: 1;}} }}
        
        /* Token Stream */
        .token-stream {{ display: flex; flex-wrap: wrap; gap: 5px; font-family: monospace; font-size: 0.8em; }}
        .token {{ padding: 2px 6px; border-radius: 4px; background: #eee; border: 1px solid #ddd; }}
        .token-type {{ color: #888; font-size: 0.7em; display: block; }}
        .token-val {{ font-weight: bold; color: #333; }}
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

    def _visualize_lexer(self, code):
        tokens_html = ""
        try:
            tokens = list(tokenize.tokenize(io.BytesIO(code.encode('utf-8')).readline))
            for tok in tokens:
                if tok.type == tokenize.ENCODING or tok.type == tokenize.ENDMARKER or tok.type == tokenize.NL:
                    continue
                tok_name = tokenize.tok_name[tok.type]
                tok_val = tok.string.replace("<", "&lt;").replace(">", "&gt;")
                if tok.type == tokenize.NEWLINE: tok_val = "\\n"
                
                tokens_html += f'<div class="token"><span class="token-type">{tok_name}</span><span class="token-val">{tok_val}</span></div>'
        except Exception as e:
            tokens_html = f"Error tokenizing: {e}"
        return tokens_html

    def _visualize_parser(self, code):
        try:
            tree = ast.parse(code)
            return ast.dump(tree, indent=4)
        except Exception as e:
            return f"Error parsing: {e}"

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
