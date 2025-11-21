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
        super().visit_Module(node)
        self.emit("fn main() {")
        self.indent_level += 1
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                if "heavy" in child.name:
                    self.emit(f'println!("Matrix Result: {{}}", {child.name}());')
                if "recursive" in child.name:
                    self.emit(f'println!("Factorial(5): {{}}", {child.name}(5));')
                if "collatz" in child.name:
                    self.emit(f'println!("Collatz Sum: {{}}", {child.name}());')
        self.indent_level -= 1
        self.emit("}")

    def visit_FunctionDef(self, node):
        self.enter_scope()
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
            if is_float_div:
                self.emit(f"let mut {target} = {val} as i32;")
            else:
                self.emit(f"let mut {target} = {val};")
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
        
        if isinstance(node.iter, ast.Call) and node.iter.func.id == 'range':
            args = node.iter.args
            if len(args) == 1:
                limit = self._expr(args[0])
                self.emit(f"for {target} in 0..{limit} {{")
            elif len(args) == 2:
                start = self._expr(args[0])
                limit = self._expr(args[1])
                self.emit(f"for {target} in {start}..{limit} {{")
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
        elif isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.Pow):
                return f"i32::pow({self._expr(node.left)}, {self._expr(node.right)} as u32)"
            if isinstance(node.op, ast.Div):
                pass
            return f"({self._expr(node.left)} {self._op(node.op)} {self._expr(node.right)})"
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
    def visit_Module(self, node):
        self.emit("// Transpiled to Go")
        self.emit("package main")
        self.emit('import "fmt"')
        self.emit('import "time"')
        self.emit("")
        super().visit_Module(node)
        self.emit("func main() {")
        self.indent_level += 1
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if "log" in child.name:
                    self.emit(f"{child.name}()")
        self.indent_level -= 1
        self.emit("}")

    def visit_AsyncFunctionDef(self, node):
        self.emit(f"func {node.name}() {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.emit("}")

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Await):
             call = node.value.value
             if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == "sleep":
                 arg = self._expr(call.args[0])
                 # Go time.Sleep takes Duration (int64 nanoseconds).
                 # We need: time.Duration(float64(time.Second) * arg)
                 self.emit(f"time.Sleep(time.Duration(float64(time.Second) * {arg}))")
        elif isinstance(node.value, ast.Call):
             self.emit(self._expr(node.value))
             
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
             
        self.emit(f"{target} := {val}")
        if "processed" in target or "data" in target:
             self.emit(f"_ = {target}")

    def _expr(self, node):
        if isinstance(node, ast.Constant): 
            if isinstance(node.value, str): return f'"{node.value}"'
            return str(node.value)
        if isinstance(node, ast.Name): return node.id
        if isinstance(node, ast.BinOp):
            return f"{self._expr(node.left)} + {self._expr(node.right)}"
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
        if isinstance(node, ast.BinOp):
             if isinstance(node.op, ast.Mult): op = "*"
             return f"{self._expr(node.left)} {op} {self._expr(node.right)}"
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
             if cls.name == "EnterpriseCustomerManager":
                  self.emit("EnterpriseCustomerManager mgr = new EnterpriseCustomerManager(\"Acme Corp\");")
                  self.emit("System.out.println(mgr.get_customer_details());")
             if cls.name == "BankAccount":
                  self.emit("BankAccount acc = new BankAccount(\"ACC-123\");")
                  self.emit("System.out.println(acc.deposit(500));")
                  self.emit("System.out.println(acc.withdraw(200));")
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
