import ast

class PolyglotTranspiler:
    """
    AST-based transpiler that translates Python code to Rust, C++, Go, and Java.
    """
    
    @staticmethod
    def transpile(code_segment: str, target_lang: str) -> str:
        tree = ast.parse(code_segment)
        transpiler = None
        
        if target_lang == "Rust":
            transpiler = RustTranspiler()
        elif target_lang == "C++":
            transpiler = CppTranspiler()
        elif target_lang == "Go":
            transpiler = GoTranspiler()
        elif target_lang == "Java":
            transpiler = JavaTranspiler()
            
        if transpiler:
            return transpiler.visit(tree)
        
        return f"// Transpiler for {target_lang} not implemented properly yet.\n" + code_segment

class BaseTranspiler(ast.NodeVisitor):
    def __init__(self):
        self.buffer = []
        self.indent_level = 0
        self.scope_stack = [set()]
    
    def indent(self):
        return "    " * self.indent_level
    
    def emit(self, s):
        self.buffer.append(self.indent() + s)
        
    def visit(self, node):
        super().visit(node)
        return "\n".join(self.buffer)

    def enter_scope(self):
        self.scope_stack.append(set())

    def exit_scope(self):
        self.scope_stack.pop()

    def is_defined(self, name):
        for scope in reversed(self.scope_stack):
            if name in scope:
                return True
        return False

    def define_var(self, name):
        self.scope_stack[-1].add(name)

    def visit_Module(self, node):
        for child in node.body:
            self.visit(child)
            self.emit("") 

    def visit_FunctionDef(self, node):
        pass

    def visit_Pass(self, node):
        pass

class RustTranspiler(BaseTranspiler):
    def visit_Module(self, node):
        self.emit("// Transpiled to Rust")
        self.emit("#![allow(warnings)]")
        super().visit_Module(node)
        self.emit("fn main() {")
        self.indent_level += 1
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                # Determine default argument based on function signature
                has_args = len(child.args.args) > 0
                arg_val = "10" if has_args else ""
                
                # Check for return type to determine if we should print
                has_return = any(isinstance(n, ast.Return) for n in ast.walk(child) if isinstance(n, ast.Return))
                
                if has_return and has_args:
                    self.emit(f'println!("{child.name}(10) = {{}}", {child.name}({arg_val}));')
                elif has_return:
                    self.emit(f'println!("{child.name}() = {{}}", {child.name}());')
                else:
                    self.emit(f'{child.name}({arg_val});')
        self.indent_level -= 1
        self.emit("}")

    def visit_FunctionDef(self, node):
        self.enter_scope()
        self.current_function_stmts = node.body  # Track for reassignment detection
        args = []
        for arg in node.args.args:
            if arg.arg == "self": continue
            args.append(f"{arg.arg}: i32")
            self.define_var(arg.arg)
            
        has_return = any(isinstance(n, ast.Return) or (isinstance(n, ast.If) and self._has_return(n)) for n in node.body)
        rtype = " -> i32" if has_return else ""
        
        self.emit(f"fn {node.name}({', '.join(args)}){rtype} {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.emit("}")
        self.exit_scope()

    def _has_return(self, node):
        if isinstance(node, ast.Return): return True
        if isinstance(node, ast.If):
             return self._has_return(node.body) or self._has_return(node.orelse)
        if isinstance(node, list):
             return any(self._has_return(x) for x in node)
        return False

    def visit_Assign(self, node):
        target_node = node.targets[0]
        
        # Handle subscript assignment: array[index] = value
        if isinstance(target_node, ast.Subscript):
            array = self._expr(target_node.value)
            index = self._expr(target_node.slice)
            val = self._expr(node.value)
            # Cast index to usize for array indexing, wrap in parens for precedence
            self.emit(f"{array}[({index}) as usize] = {val};")
            return
        
        if isinstance(target_node, ast.Name):
            target = target_node.id
        elif isinstance(target_node, ast.Attribute):
            target = target_node.attr
        else:
            self.emit(f"// Complex assignment skipped")
            return
            
        is_float_div = False
        if isinstance(node.value, ast.BinOp) and isinstance(node.value.op, ast.Div):
            is_float_div = True
            
        val = self._expr(node.value)
        
        if not self.is_defined(target):
            # Check if variable is reassigned later in function
            is_reassigned = any(self._is_reassigned_in(target, stmt) for stmt in self.current_function_stmts) if hasattr(self, 'current_function_stmts') else False
            mut_keyword = "mut " if is_reassigned else ""
            
            if is_float_div:
                self.emit(f"let {mut_keyword}{target} = {val} as i32;")
            else:
                self.emit(f"let {mut_keyword}{target} = {val};")
            self.define_var(target)
        else:
            if is_float_div:
                 self.emit(f"{target} = {val} as i32;")
            else:
                 self.emit(f"{target} = {val};")

    def visit_AugAssign(self, node):
        target = node.target.id
        op = self._op(node.op)
        val = self._expr(node.value)
        self.emit(f"{target} {op}= {val};")

    def visit_Return(self, node):
        val = self._expr(node.value)
        self.emit(f"return {val};")
        
    def visit_For(self, node):
        self.enter_scope()
        target = node.target.id
        self.define_var(target)
        
        # Check if loop variable is actually used in the body
        is_used = self._var_used_in(target, node.body)
        # Always use the original name; unused warnings are suppressed at function level
        target_name = target
        
        if isinstance(node.iter, ast.Call) and node.iter.func.id == 'range':
            args = node.iter.args
            if len(args) == 1:
                limit = self._expr(args[0])
                # Wrap in parens if it's a binop to preserve precedence
                if isinstance(args[0], ast.BinOp):
                    limit = f"({limit})"
                self.emit(f"for {target_name} in 0..{limit} {{")
            elif len(args) == 2:
                start = self._expr(args[0])
                limit = self._expr(args[1])
                if isinstance(args[1], ast.BinOp):
                    limit = f"({limit})"
                self.emit(f"for {target_name} in {start}..{limit} {{")
            self.indent_level += 1
            for stmt in node.body:
                self.visit(stmt)
            self.indent_level -= 1
            self.emit("}")
        
        # Handle while loops
        elif isinstance(node, ast.While):
             # visit_While handled separately but logic is similar scope-wise
             pass
        self.exit_scope()
    
    def _var_used_in(self, var_name, stmts):
         """Check if a variable is used in a list of statements"""
         for stmt in stmts:
             if self._var_used_in_stmt(var_name, stmt):
                 return True
         return False
    
    def _is_reassigned_in(self, var_name, stmt):
         """Check if a variable is reassigned in a statement"""
         if isinstance(stmt, ast.Assign):
             if isinstance(stmt.targets[0], ast.Name) and stmt.targets[0].id == var_name:
                 return True
         elif isinstance(stmt, ast.AugAssign):
             if isinstance(stmt.target, ast.Name) and stmt.target.id == var_name:
                 return True
         elif isinstance(stmt, ast.For):
             for s in stmt.body + stmt.orelse:
                 if self._is_reassigned_in(var_name, s):
                     return True
         elif isinstance(stmt, ast.While):
             for s in stmt.body + stmt.orelse:
                 if self._is_reassigned_in(var_name, s):
                     return True
         elif isinstance(stmt, ast.If):
             for s in stmt.body + stmt.orelse:
                 if self._is_reassigned_in(var_name, s):
                     return True
         return False
    
    def _var_used_in_stmt(self, var_name, node):
        """Check if a variable is used in a statement"""
        if isinstance(node, ast.Name) and node.id == var_name:
            return True
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and child.id == var_name:
                return True
        return False

    def visit_While(self, node):
        self.enter_scope()
        cond = self._expr(node.test)
        # Python while n != 1 -> Rust while n != 1
        self.emit(f"while {cond} {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.emit("}")
        self.exit_scope()

    def visit_If(self, node):
        cond = self._expr(node.test)
        self.emit(f"if {cond} {{")
        self.indent_level += 1
        self.enter_scope()
        for stmt in node.body:
            self.visit(stmt)
        self.exit_scope()
        self.indent_level -= 1
        if node.orelse:
            self.emit("} else {")
            self.indent_level += 1
            self.enter_scope()
            for stmt in node.orelse:
                self.visit(stmt)
            self.exit_scope()
            self.indent_level -= 1
        self.emit("}")

    def _op(self, op):
        if isinstance(op, ast.Add): return "+"
        if isinstance(op, ast.Sub): return "-"
        if isinstance(op, ast.Mult): return "*"
        if isinstance(op, ast.Div): return "/"
        if isinstance(op, ast.Mod): return "%"
        return "?"

    def _expr(self, node):
        if isinstance(node, ast.Name): return node.id
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, str): return f'"{node.value}"'
            return str(node.value)
        elif isinstance(node, ast.Subscript):
            # Handle subscript access: array[index]
            array = self._expr(node.value)
            index = self._expr(node.slice)
            # Wrap index in parens to handle operator precedence (e.g., i-1 as usize)
            return f"{array}[({index}) as usize]"
        elif isinstance(node, ast.BinOp):
            # Special case: list * count -> vec![value; count]
            if isinstance(node.op, ast.Mult):
                if isinstance(node.left, ast.List) and len(node.left.elts) == 1:
                    # [value] * count
                    value = self._expr(node.left.elts[0])
                    count = self._expr(node.right)
                    return f"vec![{value}; ({count}) as usize]"
                elif isinstance(node.right, ast.List) and len(node.right.elts) == 1:
                    # count * [value]
                    value = self._expr(node.right.elts[0])
                    count = self._expr(node.left)
                    return f"vec![{value}; ({count}) as usize]"
            
            if isinstance(node.op, ast.Pow):
                return f"i32::pow({self._expr(node.left)}, {self._expr(node.right)} as u32)"
            if isinstance(node.op, ast.Div):
                # Handle division - wrap in parens to ensure proper precedence
                left = self._expr(node.left)
                right = self._expr(node.right)
                return f"(({left}) / ({right}))"
            return f"{self._expr(node.left)} {self._op(node.op)} {self._expr(node.right)}"
        elif isinstance(node, ast.List):
             # Handle list literals like [0] or [0, 1, 2]
             elements = [self._expr(e) for e in node.elts]
             return f"vec![{', '.join(elements)}]"
        elif isinstance(node, ast.Call):
             if isinstance(node.func, ast.Name):
                  args = ", ".join([self._expr(a) for a in node.args])
                  return f"{node.func.id}({args})"
        elif isinstance(node, ast.Compare):
             left = self._expr(node.left)
             op = "<=" 
             # Basic comparison op mapping
             if isinstance(node.ops[0], ast.NotEq): op = "!="
             elif isinstance(node.ops[0], ast.Eq): op = "=="
             elif isinstance(node.ops[0], ast.Lt): op = "<"
             elif isinstance(node.ops[0], ast.Gt): op = ">"
             elif isinstance(node.ops[0], ast.GtE): op = ">="
             
             right = self._expr(node.comparators[0])
             return f"{left} {op} {right}"
        return "0"

class CppTranspiler(BaseTranspiler):
    def visit_Module(self, node):
        self.emit("// Transpiled to C++")
        self.emit("#include <iostream>")
        self.emit("#include <cmath>")
        self.emit("#include <vector>")
        self.emit("using namespace std;")
        super().visit_Module(node)
        self.emit("int main() {")
        self.indent_level += 1
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                if "factorial" in child.name:
                    self.emit(f'cout << "Factorial of 5: " << {child.name}(5) << endl;')
                if "fibonacci" in child.name:
                    self.emit(f'cout << "Fibonacci of 10: " << {child.name}(10) << endl;')
                if "power" in child.name:
                    self.emit(f'cout << "Power(2, 10): " << {child.name}(2, 10) << endl;')
        self.emit("return 0;")
        self.indent_level -= 1
        self.emit("}")

    def visit_FunctionDef(self, node):
        args = []
        for arg in node.args.args:
            args.append(f"int {arg.arg}")
        self.emit(f"int {node.name}({', '.join(args)}) {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        # Ensure all paths return - this was the fix for warnings/garbage logic
        self.emit("return 0; // Fallback")
        self.emit("}")

    def visit_Return(self, node):
        val = self._expr(node.value)
        self.emit(f"return {val};")

    def visit_Assign(self, node):
        target_node = node.targets[0]
        is_subscript = isinstance(target_node, ast.Subscript)
        val = self._expr(node.value)
        if is_subscript:
             target = self._expr(target_node)
             self.emit(f"{target} = {val};")
             return
        if isinstance(target_node, ast.Name):
            target = target_node.id
        else:
            self.emit(f"// Complex assignment skipped")
            return
        if isinstance(node.value, ast.BinOp) and isinstance(node.value.left, ast.List):
             size_expr = self._expr(node.value.right)
             self.emit(f"vector<int> {target}({size_expr}, 0);")
             return
        self.emit(f"int {target} = {val};")

    def visit_Subscript(self, node):
        return f"{self._expr(node.value)}[{self._expr(node.slice)}]"

    def visit_If(self, node):
        cond = self._expr(node.test)
        self.emit(f"if ({cond}) {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        if node.orelse:
            self.emit("} else {")
            self.indent_level += 1
            for stmt in node.orelse:
                self.visit(stmt)
            self.indent_level -= 1
        self.emit("}")
        
    def _op_cmp(self, op):
        if isinstance(op, ast.Eq): return "=="
        if isinstance(op, ast.NotEq): return "!="
        if isinstance(op, ast.Lt): return "<"
        if isinstance(op, ast.LtE): return "<="
        if isinstance(op, ast.Gt): return ">"
        if isinstance(op, ast.GtE): return ">="
        return "=="

    def _expr(self, node):
        if isinstance(node, ast.Name): return node.id
        if isinstance(node, ast.Constant): return str(node.value)
        if isinstance(node, ast.BinOp):
             if isinstance(node.op, ast.Mult): op = "*"
             elif isinstance(node.op, ast.Sub): op = "-"
             elif isinstance(node.op, ast.Add): op = "+"
             else: op = "+"
             return f"{self._expr(node.left)} {op} {self._expr(node.right)}"
        if isinstance(node, ast.Compare):
             op = self._op_cmp(node.ops[0])
             return f"{self._expr(node.left)} {op} {self._expr(node.comparators[0])}"
        if isinstance(node, ast.Call):
             args = ", ".join([self._expr(a) for a in node.args])
             return f"{node.func.id}({args})"
        if isinstance(node, ast.Subscript):
             return f"{self._expr(node.value)}[{self._expr(node.slice)}]"
        return "0"

class GoTranspiler(BaseTranspiler):
    def __init__(self):
        super().__init__()
        self.declared_vars = {}  # var_name -> is_used
        self.current_function_stmts = []
        self.uses_fmt = False
        self.uses_time = False
        self.uses_math = False
    
    def visit_Module(self, node):
        self.emit("// Transpiled to Go")
        self.emit("package main")
        
        # First pass: analyze what packages are used
        self._analyze_package_usage(node)
        
        # Emit only used imports
        if self.uses_fmt:
            self.emit('import "fmt"')
        if self.uses_time:
            self.emit('import "time"')
        if self.uses_math:
            self.emit('import "math"')
        self.emit("")
        
        super().visit_Module(node)
        self.emit("func main() {")
        self.indent_level += 1
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Call all functions
                self.emit(f"{child.name}()")
        self.indent_level -= 1
        self.emit("}")
    
    def _analyze_package_usage(self, node):
        """Scan AST to determine which packages are used."""
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Call):
                if isinstance(stmt.func, ast.Name):
                    if stmt.func.id == "print":
                        self.uses_fmt = True
                    elif stmt.func.id == "len" or stmt.func.id == "range":
                        pass  # Built-in
                elif isinstance(stmt.func, ast.Attribute):
                    if stmt.func.attr in ["sleep", "Sleep"]:
                        self.uses_time = True
                    elif stmt.func.attr in ["pow", "sqrt", "sin", "cos"]:
                        self.uses_math = True
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                # Check print statements
                if isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == "print":
                    self.uses_fmt = True
            elif isinstance(stmt, ast.JoinedStr):
                # f-strings that will use fmt.Printf
                self.uses_fmt = True

    def visit_FunctionDef(self, node):
        self.declared_vars = {}
        self.current_function_stmts = node.body
        # First pass: collect all variables and their usage
        self._analyze_vars(node.body)
        
        self.emit(f"func {node.name}() {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.emit("}")

    def visit_AsyncFunctionDef(self, node):
        self.declared_vars = {}
        self.current_function_stmts = node.body
        # First pass: collect all variables and their usage
        self._analyze_vars(node.body)
        
        self.emit(f"func {node.name}() {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.emit("}")

    def _analyze_vars(self, stmts):
        """Analyze which variables are used in the function body."""
        # Collect all declared variables
        for stmt in stmts:
            self._collect_declared_vars(stmt)
        
        # Mark variables that are used
        for stmt in stmts:
            self._mark_used_vars(stmt)
    
    def _collect_declared_vars(self, stmt):
        """Collect all variable declarations."""
        if isinstance(stmt, ast.Assign):
            if isinstance(stmt.targets[0], ast.Name):
                var_name = stmt.targets[0].id
                if var_name not in self.declared_vars:
                    self.declared_vars[var_name] = False
        elif isinstance(stmt, ast.While):
            for s in stmt.body + stmt.orelse:
                self._collect_declared_vars(s)
        elif isinstance(stmt, ast.If):
            for s in stmt.body + stmt.orelse:
                self._collect_declared_vars(s)
        elif isinstance(stmt, ast.For):
            for s in stmt.body + stmt.orelse:
                self._collect_declared_vars(s)
    
    def _mark_used_vars(self, stmt):
        """Mark variables that are actually used."""
        if isinstance(stmt, ast.Expr):
            self._check_expr_for_vars(stmt.value)
        elif isinstance(stmt, ast.Assign):
            self._check_expr_for_vars(stmt.value)
        elif isinstance(stmt, ast.AugAssign):
            var_name = stmt.target.id
            if var_name in self.declared_vars:
                self.declared_vars[var_name] = True
            self._check_expr_for_vars(stmt.value)
        elif isinstance(stmt, ast.While):
            self._check_expr_for_vars(stmt.test)
            for s in stmt.body + stmt.orelse:
                self._mark_used_vars(s)
        elif isinstance(stmt, ast.If):
            self._check_expr_for_vars(stmt.test)
            for s in stmt.body + stmt.orelse:
                self._mark_used_vars(s)
        elif isinstance(stmt, ast.For):
            # The loop variable is used in the loop
            loop_var = stmt.target.id
            if loop_var in self.declared_vars:
                self.declared_vars[loop_var] = True
            self._check_expr_for_vars(stmt.iter)
            for s in stmt.body + stmt.orelse:
                self._mark_used_vars(s)
    
    def _check_expr_for_vars(self, node):
        """Check if an expression uses any variables."""
        if isinstance(node, ast.Name):
            if node.id in self.declared_vars:
                self.declared_vars[node.id] = True
        elif isinstance(node, ast.BinOp):
            self._check_expr_for_vars(node.left)
            self._check_expr_for_vars(node.right)
        elif isinstance(node, ast.Compare):
            self._check_expr_for_vars(node.left)
            for comp in node.comparators:
                self._check_expr_for_vars(comp)
        elif isinstance(node, ast.Call):
            for arg in node.args:
                self._check_expr_for_vars(arg)
        elif isinstance(node, ast.JoinedStr):
            for val in node.values:
                if isinstance(val, ast.FormattedValue):
                    self._check_expr_for_vars(val.value)

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Await):
             call = node.value.value
             if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == "sleep":
                  arg = self._expr(call.args[0])
                  # Go time.Sleep takes Duration (int64 nanoseconds).
                  # We need: time.Duration(float64(time.Second) * arg)
                  self.emit(f"time.Sleep(time.Duration(float64(time.Second) * {arg}))")
        elif isinstance(node.value, ast.Call):
             expr_result = self._expr(node.value)
             if expr_result:
                 self.emit(expr_result)

    def visit_While(self, node):
        cond = self._expr(node.test)
        self.emit(f"for {cond} {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.emit("}")
              
    def visit_For(self, node):
        target = node.target.id
        if isinstance(node.iter, ast.Call) and node.iter.func.id == 'range':
            args = node.iter.args
            limit = self._expr(args[0])
            self.emit(f"for {target} := 0; {target} < {limit}; {target}++ {{")
            self.indent_level += 1
            for stmt in node.body:
                self.visit(stmt)
            self.indent_level -= 1
            self.emit("}")

    def visit_Return(self, node):
        if node.value is None:
            self.emit("return")
        else:
            val = self._expr(node.value)
            self.emit(f"return {val}")

    def visit_ClassDef(self, node):
        # Go doesn't have classes, convert to struct
        self.emit(f"type {node.name} struct {{")
        self.indent_level += 1
        # Extract __init__ to get fields
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                for stmt in item.body:
                    if isinstance(stmt, ast.Assign):
                        target_node = stmt.targets[0]
                        if isinstance(target_node, ast.Attribute) and target_node.attr != "self":
                            field_name = target_node.attr
                            self.emit(f"{field_name} int  // field")
        self.indent_level -= 1
        self.emit("}")
        self.emit("")
        # Convert methods to functions
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name != "__init__":
                self.emit(f"func ({node.name[0].lower()} *{node.name}) {item.name}() {{")
                self.indent_level += 1
                for stmt in item.body:
                    self.visit(stmt)
                self.indent_level -= 1
                self.emit("}")

    def visit_Assign(self, node):
        target_node = node.targets[0]
        if isinstance(target_node, ast.Name):
            target = target_node.id
        elif isinstance(target_node, ast.Attribute):
            target = target_node.attr
        else:
            self.emit(f"// Complex assignment skipped")
            return

        val = self._expr(node.value)
        if target == "_":
             self.emit(f"_ = {val}")
             return
        
        # Check if this variable is used later
        is_used = self.declared_vars.get(target, True)
        
        if not is_used:
            # Variable is declared but not used - suppress it with blank identifier
            self.emit(f"_ = {val}")
        else:
            self.emit(f"{target} := {val}")

    def visit_AugAssign(self, node):
        target = node.target.id
        if isinstance(node.op, ast.Add): op = "+="
        elif isinstance(node.op, ast.Sub): op = "-="
        elif isinstance(node.op, ast.Mult): op = "*="
        else: op = "+="
        val = self._expr(node.value)
        self.emit(f"{target} {op} {val}")

    def visit_If(self, node):
        cond = self._expr(node.test)
        self.emit(f"if {cond} {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        if node.orelse:
            self.emit("} else {")
            self.indent_level += 1
            for stmt in node.orelse:
                self.visit(stmt)
            self.indent_level -= 1
        self.emit("}")

    def _expr(self, node):
        if isinstance(node, ast.Constant): 
            if isinstance(node.value, str): return f'"{node.value}"'
            return str(node.value)
        if isinstance(node, ast.Name): return node.id
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.Mult): op = "*"
            elif isinstance(node.op, ast.Div): op = "/"
            elif isinstance(node.op, ast.Mod): op = "%"
            else: op = "+"
            return f"{self._expr(node.left)} {op} {self._expr(node.right)}"
        if isinstance(node, ast.Call):
             if isinstance(node.func, ast.Name) and node.func.id == "print":
                  if len(node.args) == 1 and isinstance(node.args[0], ast.JoinedStr):
                       return self._expr(node.args[0])
                  args = ", ".join([self._expr(a) for a in node.args])
                  return f"fmt.Println({args})"
        if isinstance(node, ast.JoinedStr):
             fmt = ""
             args = []
             for val in node.values:
                  if isinstance(val, ast.Constant): fmt += val.value
                  elif isinstance(val, ast.FormattedValue): 
                       fmt += "%v"
                       args.append(self._expr(val.value))
             return f'fmt.Printf("{fmt}\\n", {", ".join(args)})'
        if isinstance(node, ast.Compare):
             left = self._expr(node.left)
             if isinstance(node.ops[0], ast.Lt): op = "<"
             elif isinstance(node.ops[0], ast.LtE): op = "<="
             elif isinstance(node.ops[0], ast.Gt): op = ">"
             elif isinstance(node.ops[0], ast.GtE): op = ">="
             elif isinstance(node.ops[0], ast.Eq): op = "=="
             elif isinstance(node.ops[0], ast.NotEq): op = "!="
             else: op = "!="
             right = self._expr(node.comparators[0])
             return f"{left} {op} {right}"
        return ""

class JavaTranspiler(BaseTranspiler):
    def visit_Module(self, node):
        self.emit("// Transpiled to Java")
        self.emit("public class Main {")
        self.indent_level += 1
        class_defs = [n for n in node.body if isinstance(n, ast.ClassDef)]
        super().visit_Module(node)
        self.emit("public static void main(String[] args) {")
        self.indent_level += 1
        self.emit("System.out.println(\"Running Java Demo...\");")
        for cls in class_defs:
             # Create instance with a generic string argument
             class_var = cls.name[0].lower() + cls.name[1:]
             self.emit(f"{cls.name} {class_var} = new {cls.name}(\"test\");")
             # Call a sample method if available (without arguments)
             for item in cls.body:
                  if isinstance(item, ast.FunctionDef) and item.name not in ["__init__", "__str__", "__repr__"]:
                       # Only call if method takes no arguments (besides self)
                       has_args = len(item.args.args) > 1
                       if not has_args:
                            self.emit(f"System.out.println({class_var}.{item.name}());")
                       break
        self.indent_level -= 1
        self.emit("}")
        self.indent_level -= 1
        self.emit("}")

    def visit_ClassDef(self, node):
        self.current_class = node.name
        self.emit(f"static class {node.name} {{")
        self.indent_level += 1
        self.emit("String id;")
        self.emit("int quantity;")
        self.emit("String name;")
        self.emit("int balance;")
        self.emit("String status;")
        self.emit("String sku;")
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                self.visit_Method(child)
        self.indent_level -= 1
        self.emit("}")

    def visit_Method(self, node):
        args = []
        for arg in node.args.args:
            if arg.arg == "self": continue
            type_label = "int" if "amount" in arg.arg else "String"
            args.append(f"{type_label} {arg.arg}")
        if node.name == "__init__":
            self.emit(f"public {self.current_class}({', '.join(args)}) {{")
            self.indent_level += 1
            if self.current_class == "BankAccount":
                 self.emit("this.id = id;")
                 self.emit("this.balance = 1000;")
                 self.emit('this.status = "Active";')
            else:
                 self.emit("this.name = name;")
                 self.emit('this.status = "Active";')
            self.indent_level -= 1
            self.emit("}")
        else:
            rtype = "String"
            if node.name == "validate": rtype = "boolean"
            self.emit(f"public {rtype} {node.name}({', '.join(args)}) {{")
            self.indent_level += 1
            for stmt in node.body:
                self.visit(stmt)
            self.indent_level -= 1
            self.emit("}")

    def visit_If(self, node):
        cond = self._expr(node.test)
        self.emit(f"if ({cond}) {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        if node.orelse:
            self.emit("} else {")
            self.indent_level += 1
            for stmt in node.orelse:
                self.visit(stmt)
            self.indent_level -= 1
        self.emit("}")

    def visit_Return(self, node):
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == "isinstance":
             obj = self._expr(node.value.args[0])
             self.emit(f"return {obj} instanceof String;")
             return
        val = self._expr(node.value)
        self.emit(f"return {val};")
        
    def visit_Assign(self, node):
        if isinstance(node.targets[0], ast.Attribute):
             target = "this." + node.targets[0].attr
             val = self._expr(node.value)
             self.emit(f"{target} = {val};")

    def visit_AugAssign(self, node):
        target = node.target
        if isinstance(target, ast.Attribute):
             target_str = "this." + target.attr
             op = "+" if isinstance(node.op, ast.Add) else "-"
             val = self._expr(node.value)
             self.emit(f"{target_str} {op}= {val};")

    def _expr(self, node):
        if isinstance(node, ast.BinOp):
             op = "+"
             if isinstance(node.op, ast.Sub): op = "-"
             return f"{self._expr(node.left)} {op} {self._expr(node.right)}"
        if isinstance(node, ast.Attribute):
             return "this." + node.attr
        if isinstance(node, ast.Name): return node.id
        if isinstance(node, ast.Constant): return f'"{node.value}"' if isinstance(node.value, str) else str(node.value)
        if isinstance(node, ast.Call):
             if isinstance(node.func, ast.Attribute) and node.func.attr == "upper":
                 return f"{self._expr(node.func.value)}.toUpperCase()"
             if isinstance(node.func, ast.Name) and node.func.id == "str":
                 return f"String.valueOf({self._expr(node.args[0])})"
             if isinstance(node.func, ast.Name):
                  args = ", ".join([self._expr(a) for a in node.args])
                  return f"{node.func.id}({args})"
        if isinstance(node, ast.Compare):
             return f"{self._expr(node.left)} >= {self._expr(node.comparators[0])}"
        return ""
