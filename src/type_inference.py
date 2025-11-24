import ast

class TypeInference(ast.NodeVisitor):
    """
    Infers types of variables in a function/module scope.
    Types: 'int', 'float', 'str', 'bool', 'List[int]', 'unknown'
    """
    def __init__(self):
        self.types = {} # name -> type

    def infer(self, node):
        self.visit(node)
        return self.types

    def visit_Assign(self, node):
        target = node.targets[0]
        if isinstance(target, ast.Name):
            var_name = target.id
            inferred_type = self._get_type(node.value)
            # Simple union/overwrite logic
            self.types[var_name] = inferred_type
        elif isinstance(target, ast.Attribute):
            # Handle self.x
            pass

    def visit_FunctionDef(self, node):
        # Infer args if possible (not easy without calls, assume int/str based on name)
        for arg in node.args.args:
            if "name" in arg.arg or "id" in arg.arg:
                self.types[arg.arg] = "str"
            elif "amount" in arg.arg or "n" == arg.arg:
                self.types[arg.arg] = "int"
            else:
                self.types[arg.arg] = "int" # Default
        self.generic_visit(node)

    def _get_type(self, node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, int): return "int"
            if isinstance(node.value, float): return "float"
            if isinstance(node.value, str): return "str"
            if isinstance(node.value, bool): return "bool"
        
        if isinstance(node, ast.List):
            # Check elements
            if not node.elts: return "List[int]" # Default
            inner = self._get_type(node.elts[0])
            return f"List[{inner}]"
            
        if isinstance(node, ast.BinOp):
            left = self._get_type(node.left)
            right = self._get_type(node.right)
            if left == "float" or right == "float": return "float"
            if isinstance(node.op, ast.Div): return "float" # / is always float in Py3
            return "int"
            
        if isinstance(node, ast.Name):
            return self.types.get(node.id, "unknown")
            
        return "unknown"
