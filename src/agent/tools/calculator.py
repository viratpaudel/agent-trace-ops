import ast
import operator
import math
from typing import Union

# Whitelisted operators for safe arithmetic evaluation without eval() security vulnerabilities
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def _eval_node(node: ast.AST) -> Union[int, float]:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    elif isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in SAFE_OPERATORS:
            raise ValueError(f"Unsupported operator: {op_type.__name__}")
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        if op_type == ast.Div and right == 0:
            raise ZeroDivisionError("Division by zero in mathematical expression.")
        return SAFE_OPERATORS[op_type](left, right)
    elif isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in SAFE_OPERATORS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        operand = _eval_node(node.operand)
        return SAFE_OPERATORS[op_type](operand)
    elif isinstance(node, ast.Call):
        # Allow safe math functions
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in ("round", "abs", "sqrt", "ceil", "floor"):
                args = [_eval_node(arg) for arg in node.args]
                if func_name == "round":
                    return round(*args)
                elif func_name == "abs":
                    return abs(args[0])
                elif func_name == "sqrt":
                    if args[0] < 0:
                        raise ValueError("Cannot calculate square root of a negative number.")
                    return math.sqrt(args[0])
                elif func_name == "ceil":
                    return math.ceil(args[0])
                elif func_name == "floor":
                    return math.floor(args[0])
        raise ValueError("Arbitrary function execution is disabled for safety.")
    else:
        raise ValueError(f"Unsafe or invalid syntax node: {type(node).__name__}")

def safe_calculate(expression: str) -> dict:
    """Safely evaluates an arithmetic expression without arbitrary code execution."""
    cleaned = expression.strip()
    if not cleaned:
        return {"success": False, "error": "Empty expression provided."}
    try:
        parsed = ast.parse(cleaned, mode="eval")
        result = _eval_node(parsed.body)
        return {"success": True, "expression": cleaned, "result": result}
    except ZeroDivisionError as zde:
        return {"success": False, "error": f"Math error: {str(zde)}"}
    except Exception as e:
        return {"success": False, "error": f"Invalid expression: {str(e)}"}
