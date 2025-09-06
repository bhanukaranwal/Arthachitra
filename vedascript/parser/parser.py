from typing import List, Optional, Union, Any
from .ast_nodes import *
from ..lexer.lexer import Token, TokenType, VedaScriptLexer

class ParseError(Exception):
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"Parse error at line {token.line}, column {token.column}: {message}")

class VedaScriptParser:
    """
    Recursive descent parser for VedaScript language.
    Parses tokens into an Abstract Syntax Tree (AST).
    """
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        
    def parse(self) -> ProgramNode:
        """Parse the tokens into an AST."""
        statements = []
        
        while not self.is_at_end():
            if self.peek().type == TokenType.NEWLINE:
                self.advance()
                continue
                
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
        
        return ProgramNode(statements)
    
    def statement(self) -> Optional[ASTNode]:
        """Parse a statement."""
        try:
            if self.match(TokenType.FUNCTION):
                return self.function_declaration()
            elif self.match(TokenType.VAR):
                return self.variable_declaration()
            elif self.match(TokenType.IF):
                return self.if_statement()
            elif self.match(TokenType.FOR):
                return self.for_statement()
            elif self.match(TokenType.WHILE):
                return self.while_statement()
            elif self.match(TokenType.RETURN):
                return self.return_statement()
            elif self.match(TokenType.BUY, TokenType.SELL):
                return self.trade_statement()
            else:
                return self.expression_statement()
                
        except ParseError as e:
            self.synchronize()
            raise e
    
    def function_declaration(self) -> FunctionNode:
        """Parse function declaration."""
        name = self.consume(TokenType.IDENTIFIER, "Expected function name").value
        
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after function name")
        
        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            parameters.append(self.consume(TokenType.IDENTIFIER, "Expected parameter name").value)
            while self.match(TokenType.COMMA):
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expected parameter name").value)
        
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters")
        self.consume(TokenType.LEFT_BRACE, "Expected '{' before function body")
        
        body = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            if self.peek().type == TokenType.NEWLINE:
                self.advance()
                continue
            stmt = self.statement()
            if stmt:
                body.append(stmt)
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after function body")
        
        return FunctionNode(name, parameters, body)
    
    def variable_declaration(self) -> VariableNode:
        """Parse variable declaration."""
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
        
        initializer = None
        if self.match(TokenType.ASSIGN):
            initializer = self.expression()
        
        self.consume_statement_end()
        return VariableNode(name, initializer)
    
    def if_statement(self) -> IfNode:
        """Parse if statement."""
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'if'")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after if condition")
        
        then_branch = self.statement()
        else_branch = None
        
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        
        return IfNode(condition, then_branch, else_branch)
    
    def while_statement(self) -> WhileNode:
        """Parse while statement."""
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'while'")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after while condition")
        
        body = self.statement()
        return WhileNode(condition, body)
    
    def return_statement(self) -> ReturnNode:
        """Parse return statement."""
        value = None
        if not self.check_statement_end():
            value = self.expression()
        
        self.consume_statement_end()
        return ReturnNode(value)
    
    def trade_statement(self) -> TradeNode:
        """Parse buy/sell statement."""
        action = self.previous().type
        
        # Parse optional parameters
        message = None
        quantity = None
        
        if self.match(TokenType.LEFT_PAREN):
            if not self.check(TokenType.RIGHT_PAREN):
                # Parse message or quantity
                expr = self.expression()
                if isinstance(expr, StringLiteralNode):
                    message = expr.value
                elif isinstance(expr, NumberLiteralNode):
                    quantity = expr.value
                
                # Check for additional parameters
                if self.match(TokenType.COMMA):
                    expr2 = self.expression()
                    if quantity is None and isinstance(expr2, NumberLiteralNode):
                        quantity = expr2.value
            
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after trade parameters")
        
        self.consume_statement_end()
        return TradeNode(action.value.lower(), message, quantity)
    
    def expression_statement(self) -> ExpressionStatementNode:
        """Parse expression statement."""
        expr = self.expression()
        self.consume_statement_end()
        return ExpressionStatementNode(expr)
    
    def expression(self) -> ASTNode:
        """Parse expression."""
        return self.logical_or()
    
    def logical_or(self) -> ASTNode:
        """Parse logical OR expression."""
        expr = self.logical_and()
        
        while self.match(TokenType.IDENTIFIER) and self.previous().value.lower() == "or":
            operator = self.previous().value
            right = self.logical_and()
            expr = BinaryOpNode(expr, operator, right)
        
        return expr
    
    def logical_and(self) -> ASTNode:
        """Parse logical AND expression."""
        expr = self.equality()
        
        while self.match(TokenType.IDENTIFIER) and self.previous().value.lower() == "and":
            operator = self.previous().value
            right = self.equality()
            expr = BinaryOpNode(expr, operator, right)
        
        return expr
    
    def equality(self) -> ASTNode:
        """Parse equality expression."""
        expr = self.comparison()
        
        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator = self.previous().value
            right = self.comparison()
            expr = BinaryOpNode(expr, operator, right)
        
        return expr
    
    def comparison(self) -> ASTNode:
        """Parse comparison expression."""
        expr = self.term()
        
        while self.match(TokenType.GREATER_THAN, TokenType.GREATER_EQUAL, 
                         TokenType.LESS_THAN, TokenType.LESS_EQUAL):
            operator = self.previous().value
            right = self.term()
            expr = BinaryOpNode(expr, operator, right)
        
        return expr
    
    def term(self) -> ASTNode:
        """Parse term expression (+ -)."""
        expr = self.factor()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous().value
            right = self.factor()
            expr = BinaryOpNode(expr, operator, right)
        
        return expr
    
    def factor(self) -> ASTNode:
        """Parse factor expression (* /)."""
        expr = self.unary()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE):
            operator = self.previous().value
            right = self.unary()
            expr = BinaryOpNode(expr, operator, right)
        
        return expr
    
    def unary(self) -> ASTNode:
        """Parse unary expression."""
        if self.match(TokenType.MINUS):
            operator = self.previous().value
            right = self.unary()
            return UnaryOpNode(operator, right)
        
        return self.call()
    
    def call(self) -> ASTNode:
        """Parse function call or array access."""
        expr = self.primary()
        
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.LEFT_BRACKET):
                index = self.expression()
                self.consume(TokenType.RIGHT_BRACKET, "Expected ']' after array index")
                expr = ArrayAccessNode(expr, index)
            else:
                break
        
        return expr
    
    def finish_call(self, callee: ASTNode) -> FunctionCallNode:
        """Parse function call arguments."""
        arguments = []
        
        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append(self.expression())
            while self.match(TokenType.COMMA):
                arguments.append(self.expression())
        
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after arguments")
        
        if isinstance(callee, IdentifierNode):
            return FunctionCallNode(callee.name, arguments)
        else:
            raise ParseError("Invalid function call", self.peek())
    
    def primary(self) -> ASTNode:
        """Parse primary expression."""
        if self.match(TokenType.NUMBER):
            return NumberLiteralNode(float(self.previous().value))
        
        if self.match(TokenType.STRING):
            return StringLiteralNode(self.previous().value)
        
        if self.match(TokenType.IDENTIFIER):
            return IdentifierNode(self.previous().value)
        
        # Built-in market data functions
        if self.match(TokenType.OPEN, TokenType.HIGH, TokenType.LOW, 
                     TokenType.CLOSE, TokenType.VOLUME):
            return IdentifierNode(self.previous().value.lower())
        
        # Technical indicators
        if self.match(TokenType.SMA, TokenType.EMA, TokenType.RSI, TokenType.MACD):
            return IdentifierNode(self.previous().value.lower())
        
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression")
            return expr
        
        raise ParseError(f"Unexpected token '{self.peek().value}'", self.peek())
    
    # Helper methods
    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types."""
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        return False
    
    def check(self, token_type: TokenType) -> bool:
        """Check if current token is of given type."""
        if self.is_at_end():
            return False
        return self.peek().type == token_type
    
    def advance(self) -> Token:
        """Consume current token and return it."""
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def is_at_end(self) -> bool:
        """Check if we're at the end of tokens."""
        return self.peek().type == TokenType.EOF
    
    def peek(self) -> Token:
        """Return current token without advancing."""
        return self.tokens[self.current]
    
    def previous(self) -> Token:
        """Return previous token."""
        return self.tokens[self.current - 1]
    
    def consume(self, token_type: TokenType, message: str) -> Token:
        """Consume token of expected type or raise error."""
        if self.check(token_type):
            return self.advance()
        
        current_token = self.peek()
        raise ParseError(message, current_token)
    
    def check_statement_end(self) -> bool:
        """Check for statement end (newline or semicolon)."""
        return self.check(TokenType.NEWLINE) or self.check(TokenType.SEMICOLON) or self.is_at_end()
    
    def consume_statement_end(self):
        """Consume statement ending tokens."""
        while self.match(TokenType.NEWLINE, TokenType.SEMICOLON):
            pass
    
    def synchronize(self):
        """Synchronize parser after error."""
        self.advance()
        
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return
            
            if self.peek().type in [TokenType.FUNCTION, TokenType.VAR, TokenType.IF,
                                   TokenType.FOR, TokenType.WHILE, TokenType.RETURN]:
                return
            
            self.advance()
