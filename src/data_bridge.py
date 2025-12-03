"""
Data Bridge Module

Manages data transfer between code segments.
Each segment can declare inputs/outputs, and the bridge
ensures data flows correctly between transpiled code pieces.
"""

import json
import ast
from typing import Dict, List, Any, Set, Tuple
from dataclasses import dataclass, field

@dataclass
class VariableInfo:
    """Information about a variable"""
    name: str
    inferred_type: str  # 'int', 'float', 'str', 'list', 'dict', 'unknown'
    is_input: bool = False  # Comes from outside segment
    is_output: bool = False  # Used outside segment
    initial_value: Any = None
    line_defined: int = -1
    lines_used: List[int] = field(default_factory=list)

@dataclass
class SegmentInterface:
    """Interface for a code segment"""
    segment_id: int
    inputs: Dict[str, VariableInfo] = field(default_factory=dict)
    outputs: Dict[str, VariableInfo] = field(default_factory=dict)
    internal_vars: Dict[str, VariableInfo] = field(default_factory=dict)

class DataBridgeAnalyzer(ast.NodeVisitor):
    """Analyzes code to extract variable usage patterns"""
    
    def __init__(self, segment_id: int):
        self.segment_id = segment_id
        self.interface = SegmentInterface(segment_id)
        self.all_vars: Dict[str, VariableInfo] = {}
        self.current_scope = set()
        self.function_params = set()
        self.line_number = 0
        self.assigned_vars = set()
        self.used_vars = set()
    
    def analyze(self, tree: ast.AST) -> SegmentInterface:
        """Analyze AST and build interface"""
        # First pass: collect all assignments and usages
        self._collect_vars(tree)
        
        # Second pass: classify variables
        self._classify_vars(tree)
        
        return self.interface
    
    def _collect_vars(self, node):
        """Collect all variable assignments and uses"""
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name):
                        self.assigned_vars.add(target.id)
                    elif isinstance(target, ast.Tuple):
                        for elt in target.elts:
                            if isinstance(elt, ast.Name):
                                self.assigned_vars.add(elt.id)
            
            elif isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                self.used_vars.add(child.id)
            
            elif isinstance(child, ast.FunctionDef):
                for arg in child.args.args:
                    self.function_params.add(arg.arg)
    
    def _classify_vars(self, tree):
        """Classify variables as input, output, or internal"""
        # Variables used before assignment = inputs
        inputs = self.used_vars - self.assigned_vars - self.function_params
        
        # All assigned = internal or output
        internal = self.assigned_vars
        
        # If internal var is used after assignment, it's internal or output
        # For simplicity: all assigned vars are potentially outputs
        outputs = self.assigned_vars & self.used_vars
        
        for var_name in inputs:
            info = VariableInfo(
                name=var_name,
                inferred_type=self._infer_type(tree, var_name),
                is_input=True,
                is_output=False
            )
            self.interface.inputs[var_name] = info
        
        for var_name in internal:
            info = VariableInfo(
                name=var_name,
                inferred_type=self._infer_type(tree, var_name),
                is_input=False,
                is_output=(var_name in outputs)
            )
            self.interface.internal_vars[var_name] = info
    
    def _infer_type(self, tree: ast.AST, var_name: str) -> str:
        """Infer variable type from assignments"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == var_name:
                        return self._get_expr_type(node.value)
        return "unknown"
    
    def _get_expr_type(self, node) -> str:
        """Get type from expression"""
        if isinstance(node, ast.Constant):
            if isinstance(node.value, int):
                return "int"
            elif isinstance(node.value, float):
                return "float"
            elif isinstance(node.value, str):
                return "str"
            elif isinstance(node.value, bool):
                return "bool"
        elif isinstance(node, ast.List):
            return "list"
        elif isinstance(node, ast.Dict):
            return "dict"
        elif isinstance(node, ast.BinOp):
            left = self._get_expr_type(node.left)
            if left != "unknown":
                return left
            return self._get_expr_type(node.right)
        elif isinstance(node, ast.Name):
            return "unknown"
        return "unknown"

class DataBridge:
    """
    Manages data transfer between segments.
    Generates connector code and serialization/deserialization logic.
    """
    
    def __init__(self):
        self.segments: Dict[int, SegmentInterface] = {}
        self.data_flow: Dict[int, Dict[int, List[str]]] = {}  # from_segment -> to_segment -> variables
        self.type_mappings = {
            "int": {"python": "int", "rust": "i32", "cpp": "int", "go": "int64", "java": "int"},
            "float": {"python": "float", "rust": "f64", "cpp": "double", "go": "float64", "java": "double"},
            "str": {"python": "str", "rust": "String", "cpp": "string", "go": "string", "java": "String"},
            "bool": {"python": "bool", "rust": "bool", "cpp": "bool", "go": "bool", "java": "boolean"},
            "list": {"python": "list", "rust": "Vec", "cpp": "vector", "go": "[]", "java": "ArrayList"},
            "dict": {"python": "dict", "rust": "HashMap", "cpp": "map", "go": "map", "java": "HashMap"},
        }
    
    def register_segment(self, segment_id: int, interface: SegmentInterface):
        """Register a segment and its interface"""
        self.segments[segment_id] = interface
        self.data_flow[segment_id] = {}
    
    def analyze_dependencies(self) -> Dict[int, List[int]]:
        """
        Analyze data flow between segments.
        Returns: segment_id -> list of dependent segment_ids
        """
        dependencies = {seg_id: [] for seg_id in self.segments.keys()}
        
        for consumer_id, consumer_interface in self.segments.items():
            for input_var in consumer_interface.inputs.keys():
                # Find which segment produces this variable
                for producer_id, producer_interface in self.segments.items():
                    if producer_id == consumer_id:
                        continue
                    if input_var in producer_interface.outputs:
                        # Producer must run before consumer
                        if producer_id not in dependencies[consumer_id]:
                            dependencies[consumer_id].append(producer_id)
                        self.data_flow[producer_id][consumer_id] = [input_var]
        
        return dependencies
    
    def generate_connector(
        self,
        from_segment_id: int,
        to_segment_id: int,
        variables: List[str],
        target_lang: str = "Python"
    ) -> str:
        """
        Generate code to transfer data between segments.
        Returns connector code in target language.
        """
        from_interface = self.segments.get(from_segment_id)
        to_interface = self.segments.get(to_segment_id)
        
        if not from_interface or not to_interface:
            return "# ERROR: Invalid segments"
        
        if target_lang.lower() == "python":
            return self._python_connector(from_segment_id, to_segment_id, variables)
        elif target_lang.lower() == "rust":
            return self._rust_connector(from_segment_id, to_segment_id, variables)
        elif target_lang.lower() == "cpp":
            return self._cpp_connector(from_segment_id, to_segment_id, variables)
        elif target_lang.lower() == "go":
            return self._go_connector(from_segment_id, to_segment_id, variables)
        elif target_lang.lower() == "java":
            return self._java_connector(from_segment_id, to_segment_id, variables)
        
        return "# Unsupported language for connector"
    
    def _python_connector(self, from_id: int, to_id: int, variables: List[str]) -> str:
        """Generate Python data transfer code"""
        code = f"# === Data transfer: Segment {from_id} -> Segment {to_id} ===\n"
        from_interface = self.segments[from_id]
        
        for var in variables:
            var_info = from_interface.internal_vars.get(var) or from_interface.outputs.get(var)
            if var_info:
                code += f"# {var_info.name}: {var_info.inferred_type}\n"
        
        code += "\n"
        return code
    
    def _rust_connector(self, from_id: int, to_id: int, variables: List[str]) -> str:
        """Generate Rust data transfer code (simplified)"""
        code = f"// === Data transfer: Segment {from_id} -> Segment {to_id} ===\n"
        from_interface = self.segments[from_id]
        
        for var in variables:
            var_info = from_interface.internal_vars.get(var) or from_interface.outputs.get(var)
            if var_info:
                code += f"// Transfer {var_info.name}: {var_info.inferred_type}\n"
        
        code += "\n"
        return code
    
    def _cpp_connector(self, from_id: int, to_id: int, variables: List[str]) -> str:
        """Generate C++ data transfer code"""
        code = f"// === Data transfer: Segment {from_id} -> Segment {to_id} ===\n"
        from_interface = self.segments[from_id]
        
        for var in variables:
            var_info = from_interface.internal_vars.get(var) or from_interface.outputs.get(var)
            if var_info:
                code += f"// Transfer {var_info.name}: {var_info.inferred_type}\n"
        
        code += "\n"
        return code
    
    def _go_connector(self, from_id: int, to_id: int, variables: List[str]) -> str:
        """Generate Go data transfer code"""
        code = f"// === Data transfer: Segment {from_id} -> Segment {to_id} ===\n"
        from_interface = self.segments[from_id]
        
        for var in variables:
            var_info = from_interface.internal_vars.get(var) or from_interface.outputs.get(var)
            if var_info:
                code += f"// Transfer {var_info.name}: {var_info.inferred_type}\n"
        
        code += "\n"
        return code
    
    def _java_connector(self, from_id: int, to_id: int, variables: List[str]) -> str:
        """Generate Java data transfer code"""
        code = f"// === Data transfer: Segment {from_id} -> Segment {to_id} ===\n"
        from_interface = self.segments[from_id]
        
        for var in variables:
            var_info = from_interface.internal_vars.get(var) or from_interface.outputs.get(var)
            if var_info:
                code += f"// Transfer {var_info.name}: {var_info.inferred_type}\n"
        
        code += "\n"
        return code
    
    def generate_serialization(
        self,
        variables: Dict[str, VariableInfo],
        target_lang: str = "Python"
    ) -> Tuple[str, str]:
        """
        Generate serialization and deserialization code.
        Returns: (serialize_code, deserialize_code)
        """
        if target_lang.lower() == "python":
            serialize = "import json\n"
            for var_name, var_info in variables.items():
                if var_info.inferred_type in ["list", "dict"]:
                    serialize += f"_{var_name}_json = json.dumps({var_name})\n"
            
            deserialize = "import json\n"
            for var_name, var_info in variables.items():
                if var_info.inferred_type in ["list", "dict"]:
                    deserialize += f"{var_name} = json.loads(_{var_name}_json)\n"
            
            return serialize, deserialize
        
        # Simplified for other languages
        return "// Serialization", "// Deserialization"
    
    def get_execution_order(self) -> List[int]:
        """
        Determine execution order based on data dependencies.
        Returns: list of segment IDs in execution order
        """
        dependencies = self.analyze_dependencies()
        order = []
        visited = set()
        
        def visit(seg_id):
            if seg_id in visited:
                return
            visited.add(seg_id)
            for dep in dependencies.get(seg_id, []):
                visit(dep)
            order.append(seg_id)
        
        for seg_id in self.segments.keys():
            visit(seg_id)
        
        return order
    
    def get_data_summary(self) -> Dict:
        """Get summary of data flow between segments"""
        summary = {
            "total_segments": len(self.segments),
            "data_flows": {},
            "dependencies": self.analyze_dependencies(),
            "execution_order": self.get_execution_order()
        }
        
        for from_id, to_dict in self.data_flow.items():
            for to_id, vars in to_dict.items():
                if to_id not in summary["data_flows"]:
                    summary["data_flows"][to_id] = {}
                summary["data_flows"][to_id][from_id] = vars
        
        return summary
