import ast
from dataclasses import dataclass
from typing import Dict

@dataclass
class CodeFeatures:
    math_ops: int = 0
    io_ops: int = 0
    loops: int = 0
    conditionals: int = 0
    functions: int = 0
    classes: int = 0
    async_ops: int = 0
    recursion: bool = False
    string_ops: int = 0

class FeatureAnalyzer(ast.NodeVisitor):
    """
    Walks the AST of a code segment to extract features 
    that influence performance in different languages.
    """
    def __init__(self):
        self.features = CodeFeatures()
        self.current_func_name = None

    def analyze(self, tree: ast.AST) -> CodeFeatures:
        self.features = CodeFeatures()
        self.visit(tree)
        return self.features

    def visit_BinOp(self, node):
        # Arithmetic operations
        self.features.math_ops += 1
        self.generic_visit(node)

    def visit_Call(self, node):
        # Check for IO-like calls (print, open, read, write)
        name = ""
        if isinstance(node.func, ast.Name):
            name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            name = node.func.attr
            
        if name in ['print', 'open', 'read', 'write', 'input']:
            self.features.io_ops += 1
        else:
            self.features.functions += 1
            
        # Recursion check (naive)
        if self.current_func_name and name == self.current_func_name:
            self.features.recursion = True
            
        self.generic_visit(node)

    def visit_For(self, node):
        self.features.loops += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.features.loops += 1
        self.generic_visit(node)

    def visit_If(self, node):
        self.features.conditionals += 1
        self.generic_visit(node)
        
    def visit_AsyncFunctionDef(self, node):
        self.features.async_ops += 1
        self.visit_FunctionDef(node)

    def visit_FunctionDef(self, node):
        self.current_func_name = node.name
        self.generic_visit(node)
        self.current_func_name = None

    def visit_ClassDef(self, node):
        self.features.classes += 1
        self.generic_visit(node)

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            self.features.string_ops += 1
        self.generic_visit(node)
