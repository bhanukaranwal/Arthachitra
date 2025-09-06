import math
import statistics
from typing import Dict, List, Any, Optional, Callable
from ..parser.ast_nodes import *
from .builtins import BuiltinFunctions

class VedaScriptRuntimeError(Exception):
    def __init__(self, message: str, node: ASTNode = None):
        self.message = message
        self.node = node
        super().__init__(message)

class Environment:
    def __init__(self, parent: Optional['Environment'] = None):
        self.parent = parent
        self.variables: Dict[str, Any] = {}
        
    def define(self, name: str, value: Any):
        self.variables[name] = value
        
    def get(self, name: str) -> Any:
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name)
        raise VedaScriptRuntimeError(f"Undefined variable '{name}'")
        
    def set(self, name: str, value: Any):
        if name in self.variables:
            self.variables[name] = value
            return
        if self.parent:
            self.parent.set(name, value)
            return
        raise VedaScriptRuntimeError(f"Undefined variable '{name}'")

class VedaScriptFunction:
    def __init__(self, declaration: FunctionNode, closure: Environment):
        self.declaration = declaration
        self.closure = closure
        
    def call(self, interpreter: 'VedaScriptInterpreter', arguments: List[Any]) -> Any:
        environment = Environment(self.closure)
        
        # Bind parameters
        for i, param in enumerate(self.declaration.parameters):
            value = arguments[i] if i < len(arguments) else None
            environment.define(param, value)
            
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnValue as return_value:
            return return_value.value
            
        return None

class ReturnValue(Exception):
    def __init__(self, value: Any):
        self.value = value

class VedaScriptInterpreter:
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.market_data = {}
        self.trades = []
        self.builtins = BuiltinFunctions(self)
        
        # Initialize built-in functions
        self._init_builtins()
        
    def _init_builtins(self):
        """Initialize built-in functions and variables."""
        # Market data variables
        self.globals.define("open", self.builtins.get_open)
        self.globals.define("high", self.builtins.get_high)
        self.globals.define("low", self.builtins.get_low)
        self.globals.define("close", self.builtins.get_close)
        self.globals.define("volume", self.builtins.get_volume)
        
        # Technical indicators
        self.globals.define("sma", self.builtins.sma)
        self.globals.define("ema", self.builtins.ema)
        self.globals.define("rsi", self.builtins.rsi)
        self.globals.define("macd", self.builtins.macd)
        self.globals.define("bb", self.builtins.bollinger_bands)
        
        # Trading functions
        self.globals.define("buy", self.builtins.buy)
        self.globals.define("sell", self.builtins.sell)
        self.globals.define("position", self.builtins.get_position)
        
        # Math functions
        self.globals.define("abs", abs)
        self.globals.define("max", max)
        self.globals.define("min", min)
        self.globals.define("round", round)
        self.globals.define("sqrt", math.sqrt)
        
    def set_market_data(self, data: Dict[str, List[float]]):
        """Set market data for the interpreter."""
        self.market_data = data
        
    def interpret(self, program: ProgramNode) -> Any:
        """Interpret the AST program."""
        try:
            for statement in program.statements:
                self.execute(statement)
        except VedaScriptRuntimeError as e:
            print(f"Runtime Error: {e.message}")
            raise
            
    def execute(self, node: StatementNode) -> Any:
        """Execute a statement node."""
        if isinstance(node, ExpressionStatementNode):
            return self.evaluate(node.expression)
        elif isinstance(node, VariableNode):
            return self.execute_variable(node)
        elif isinstance(node, FunctionNode):
            return self.execute_function(node)
        elif isinstance(node, IfNode):
            return self.execute_if(node)
        elif isinstance(node, WhileNode):
            return self.execute_while(node)
        elif isinstance(node, ForNode):
            return self.execute_for(node)
        elif isinstance(node, ReturnNode):
            return self.execute_return(node)
        elif isinstance(node, TradeNode):
            return self.execute_trade(node)
        elif isinstance(node, BlockNode):
            return self.execute_block(node.statements, Environment(self.environment))
        else:
            raise VedaScriptRuntimeError(f"Unknown statement type: {type(node)}")
            
    def execute_variable(self, node: VariableNode):
        """Execute variable declaration."""
        value = None
        if node.initializer:
            value = self.evaluate(node.initializer)
        self.environment.define(node.name, value)
        
    def execute_function(self, node: FunctionNode):
        """Execute function declaration."""
        function = VedaScriptFunction(node, self.environment)
        self.environment.define(node.name, function)
        
    def execute_if(self, node: IfNode):
        """Execute if statement."""
        condition = self.evaluate(node.condition)
        if self.is_truthy(condition):
            self.execute(node.then_branch)
        elif node.else_branch:
            self.execute(node.else_branch)
            
    def execute_while(self, node: WhileNode):
        """Execute while loop."""
        while self.is_truthy(self.evaluate(node.condition)):
            self.execute(node.body)
            
    def execute_for(self, node: ForNode):
        """Execute for loop."""
        if node.initializer:
            self.execute(node.initializer)
            
        while True:
            if node.condition and not self.is_truthy(self.evaluate(node.condition)):
                break
                
            self.execute(node.body)
            
            if node.increment:
                self.evaluate(node.increment)
                
    def execute_return(self, node: ReturnNode):
        """Execute return statement."""
        value = None
        if node.value:
            value = self.evaluate(node.value)
        raise ReturnValue(value)
        
    def execute_trade(self, node: TradeNode):
        """Execute trade statement (buy/sell)."""
        trade = {
            "action": node.action,
            "message": node.message,
            "quantity": node.quantity,
            "timestamp": len(self.trades)  # Simple timestamp
        }
        self.trades.append(trade)
        print(f"Trade executed: {node.action.upper()}")
        if node.message:
            print(f"  Message: {node.message}")
        if node.quantity:
            print(f"  Quantity: {node.quantity}")
            
    def execute_block(self, statements: List[StatementNode], environment: Environment):
        """Execute block of statements."""
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous
            
    def evaluate(self, node: ExpressionNode) -> Any:
        """Evaluate an expression node."""
        if isinstance(node, NumberLiteralNode):
            return node.value
        elif isinstance(node, StringLiteralNode):
            return node.value
        elif isinstance(node, BooleanLiteralNode):
            return node.value
        elif isinstance(node, IdentifierNode):
            return self.environment.get(node.name)
        elif isinstance(node, BinaryOpNode):
            return self.evaluate_binary(node)
        elif isinstance(node, UnaryOpNode):
            return self.evaluate_unary(node)
        elif isinstance(node, FunctionCallNode):
            return self.evaluate_call(node)
        elif isinstance(node, ArrayAccessNode):
            return self.evaluate_array_access(node)
        else:
            raise VedaScriptRuntimeError(f"Unknown expression type: {type(node)}")
            
    def evaluate_binary(self, node: BinaryOpNode) -> Any:
        """Evaluate binary operation."""
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)
        
        if node.operator == "+":
            return left + right
        elif node.operator == "-":
            return left - right
        elif node.operator == "*":
            return left * right
        elif node.operator == "/":
            if right == 0:
                raise VedaScriptRuntimeError("Division by zero")
            return left / right
        elif node.operator == "==":
            return left == right
        elif node.operator == "!=":
            return left != right
        elif node.operator == "<":
            return left < right
        elif node.operator == "<=":
            return left <= right
        elif node.operator == ">":
            return left > right
        elif node.operator == ">=":
            return left >= right
        elif node.operator == "and":
            return self.is_truthy(left) and self.is_truthy(right)
        elif node.operator == "or":
            return self.is_truthy(left) or self.is_truthy(right)
        else:
            raise VedaScriptRuntimeError(f"Unknown binary operator: {node.operator}")
            
    def evaluate_unary(self, node: UnaryOpNode) -> Any:
        """Evaluate unary operation."""
        operand = self.evaluate(node.operand)
        
        if node.operator == "-":
            return -operand
        elif node.operator == "not":
            return not self.is_truthy(operand)
        else:
            raise VedaScriptRuntimeError(f"Unknown unary operator: {node.operator}")
            
    def evaluate_call(self, node: FunctionCallNode) -> Any:
        """Evaluate function call."""
        callee = self.environment.get(node.name)
        
        arguments = []
        for arg in node.arguments:
            arguments.append(self.evaluate(arg))
            
        if isinstance(callee, VedaScriptFunction):
            return callee.call(self, arguments)
        elif callable(callee):
            return callee(*arguments)
        else:
            raise VedaScriptRuntimeError(f"'{node.name}' is not a function")
            
    def evaluate_array_access(self, node: ArrayAccessNode) -> Any:
        """Evaluate array access."""
        array = self.evaluate(node.array)
        index = self.evaluate(node.index)
        
        if isinstance(array, list):
            if isinstance(index, int) and 0 <= index < len(array):
                return array[index]
            else:
                raise VedaScriptRuntimeError("Array index out of bounds")
        else:
            raise VedaScriptRuntimeError("Can only index arrays")
            
    def is_truthy(self, value: Any) -> bool:
        """Determine if a value is truthy."""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        return True
