from abc import ABC, abstractmethod
from typing import List, Any, Optional, Union

class ASTNode(ABC):
    """Base class for all AST nodes."""
    pass

class StatementNode(ASTNode):
    """Base class for all statement nodes."""
    pass

class ExpressionNode(ASTNode):
    """Base class for all expression nodes."""
    pass

class ProgramNode(ASTNode):
    def __init__(self, statements: List[StatementNode]):
        self.statements = statements

class FunctionNode(StatementNode):
    def __init__(self, name: str, parameters: List[str], body: List[StatementNode]):
        self.name = name
        self.parameters = parameters
        self.body = body

class VariableNode(StatementNode):
    def __init__(self, name: str, initializer: Optional[ExpressionNode] = None):
        self.name = name
        self.initializer = initializer

class IfNode(StatementNode):
    def __init__(self, condition: ExpressionNode, then_branch: StatementNode, 
                 else_branch: Optional[StatementNode] = None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

class WhileNode(StatementNode):
    def __init__(self, condition: ExpressionNode, body: StatementNode):
        self.condition = condition
        self.body = body

class ForNode(StatementNode):
    def __init__(self, initializer: Optional[StatementNode], condition: Optional[ExpressionNode],
                 increment: Optional[ExpressionNode], body: StatementNode):
        self.initializer = initializer
        self.condition = condition
        self.increment = increment
        self.body = body

class ReturnNode(StatementNode):
    def __init__(self, value: Optional[ExpressionNode] = None):
        self.value = value

class TradeNode(StatementNode):
    def __init__(self, action: str, message: Optional[str] = None, quantity: Optional[float] = None):
        self.action = action  # 'buy' or 'sell'
        self.message = message
        self.quantity = quantity

class ExpressionStatementNode(StatementNode):
    def __init__(self, expression: ExpressionNode):
        self.expression = expression

class BinaryOpNode(ExpressionNode):
    def __init__(self, left: ExpressionNode, operator: str, right: ExpressionNode):
        self.left = left
        self.operator = operator
        self.right = right

class UnaryOpNode(ExpressionNode):
    def __init__(self, operator: str, operand: ExpressionNode):
        self.operator = operator
        self.operand = operand

class FunctionCallNode(ExpressionNode):
    def __init__(self, name: str, arguments: List[ExpressionNode]):
        self.name = name
        self.arguments = arguments

class ArrayAccessNode(ExpressionNode):
    def __init__(self, array: ExpressionNode, index: ExpressionNode):
        self.array = array
        self.index = index

class IdentifierNode(ExpressionNode):
    def __init__(self, name: str):
        self.name = name

class NumberLiteralNode(ExpressionNode):
    def __init__(self, value: float):
        self.value = value

class StringLiteralNode(ExpressionNode):
    def __init__(self, value: str):
        self.value = value

class BooleanLiteralNode(ExpressionNode):
    def __init__(self, value: bool):
        self.value = value

class BlockNode(StatementNode):
    def __init__(self, statements: List[StatementNode]):
        self.statements = statements
