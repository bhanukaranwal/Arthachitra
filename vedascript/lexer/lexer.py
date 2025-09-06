import re
from enum import Enum
from typing import List, NamedTuple

class TokenType(Enum):
    # Literals
    NUMBER = "NUMBER"
    STRING = "STRING"
    IDENTIFIER = "IDENTIFIER"
    
    # Keywords
    IF = "IF"
    ELSE = "ELSE"
    FOR = "FOR"
    WHILE = "WHILE"
    FUNCTION = "FUNCTION"
    RETURN = "RETURN"
    VAR = "VAR"
    
    # Trading specific
    BUY = "BUY"
    SELL = "SELL"
    CLOSE = "CLOSE"
    OPEN = "OPEN"
    HIGH = "HIGH"
    LOW = "LOW"
    VOLUME = "VOLUME"
    SMA = "SMA"
    EMA = "EMA"
    RSI = "RSI"
    MACD = "MACD"
    
    # Operators
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    ASSIGN = "ASSIGN"
    EQUAL = "EQUAL"
    NOT_EQUAL = "NOT_EQUAL"
    LESS_THAN = "LESS_THAN"
    GREATER_THAN = "GREATER_THAN"
    LESS_EQUAL = "LESS_EQUAL"
    GREATER_EQUAL = "GREATER_EQUAL"
    
    # Punctuation
    LEFT_PAREN = "LEFT_PAREN"
    RIGHT_PAREN = "RIGHT_PAREN"
    LEFT_BRACE = "LEFT_BRACE"
    RIGHT_BRACE = "RIGHT_BRACE"
    LEFT_BRACKET = "LEFT_BRACKET"
    RIGHT_BRACKET = "RIGHT_BRACKET"
    COMMA = "COMMA"
    SEMICOLON = "SEMICOLON"
    
    # Special
    NEWLINE = "NEWLINE"
    EOF = "EOF"

class Token(NamedTuple):
    type: TokenType
    value: str
    line: int
    column: int

class VedaScriptLexer:
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        
        self.keywords = {
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'for': TokenType.FOR,
            'while': TokenType.WHILE,
            'function': TokenType.FUNCTION,
            'return': TokenType.RETURN,
            'var': TokenType.VAR,
            'buy': TokenType.BUY,
            'sell': TokenType.SELL,
            'close': TokenType.CLOSE,
            'open': TokenType.OPEN,
            'high': TokenType.HIGH,
            'low': TokenType.LOW,
            'volume': TokenType.VOLUME,
            'sma': TokenType.SMA,
            'ema': TokenType.EMA,
            'rsi': TokenType.RSI,
            'macd': TokenType.MACD,
        }
        
        self.operators = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '=': TokenType.ASSIGN,
            '==': TokenType.EQUAL,
            '!=': TokenType.NOT_EQUAL,
            '<': TokenType.LESS_THAN,
            '>': TokenType.GREATER_THAN,
            '<=': TokenType.LESS_EQUAL,
            '>=': TokenType.GREATER_EQUAL,
        }
        
        self.punctuation = {
            '(': TokenType.LEFT_PAREN,
            ')': TokenType.RIGHT_PAREN,
            '{': TokenType.LEFT_BRACE,
            '}': TokenType.RIGHT_BRACE,
            '[': TokenType.LEFT_BRACKET,
            ']': TokenType.RIGHT_BRACKET,
            ',': TokenType.COMMA,
            ';': TokenType.SEMICOLON,
        }

    def current_char(self) -> str:
        if self.position >= len(self.source):
            return '\0'
        return self.source[self.position]

    def peek_char(self, offset: int = 1) -> str:
        pos = self.position + offset
        if pos >= len(self.source):
            return '\0'
        return self.source[pos]

    def advance(self):
        if self.position < len(self.source) and self.source[self.position] == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.position += 1

    def skip_whitespace(self):
        while self.current_char() in ' \t\r':
            self.advance()

    def skip_comment(self):
        if self.current_char() == '/' and self.peek_char() == '/':
            while self.current_char() != '\n' and self.current_char() != '\0':
                self.advance()

    def read_number(self) -> Token:
        start_line, start_column = self.line, self.column
        value = ''
        
        while self.current_char().isdigit() or self.current_char() == '.':
            value += self.current_char()
            self.advance()
        
        return Token(TokenType.NUMBER, value, start_line, start_column)

    def read_string(self) -> Token:
        start_line, start_column = self.line, self.column
        quote_char = self.current_char()
        self.advance()  # Skip opening quote
        
        value = ''
        while self.current_char() != quote_char and self.current_char() != '\0':
            if self.current_char() == '\\':
                self.advance()
                escape_char = self.current_char()
                if escape_char == 'n':
                    value += '\n'
                elif escape_char == 't':
                    value += '\t'
                elif escape_char == 'r':
                    value += '\r'
                elif escape_char == '\\':
                    value += '\\'
                elif escape_char == quote_char:
                    value += quote_char
                else:
                    value += escape_char
            else:
                value += self.current_char()
            self.advance()
        
        if self.current_char() == quote_char:
            self.advance()  # Skip closing quote
        
        return Token(TokenType.STRING, value, start_line, start_column)

    def read_identifier(self) -> Token:
        start_line, start_column = self.line, self.column
        value = ''
        
        while self.current_char().isalnum() or self.current_char() == '_':
            value += self.current_char()
            self.advance()
        
        token_type = self.keywords.get(value.lower(), TokenType.IDENTIFIER)
        return Token(token_type, value, start_line, start_column)

    def read_operator(self) -> Token:
        start_line, start_column = self.line, self.column
        char = self.current_char()
        
        # Check for two-character operators
        if char in ['=', '!', '<', '>']:
            next_char = self.peek_char()
            two_char = char + next_char
            if two_char in self.operators:
                self.advance()
                self.advance()
                return Token(self.operators[two_char], two_char, start_line, start_column)
        
        # Single character operator
        self.advance()
        token_type = self.operators.get(char, TokenType.IDENTIFIER)
        return Token(token_type, char, start_line, start_column)

    def tokenize(self) -> List[Token]:
        while self.position < len(self.source):
            self.skip_whitespace()
            self.skip_comment()
            
            char = self.current_char()
            
            if char == '\0':
                break
            elif char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, char, self.line, self.column))
                self.advance()
            elif char.isdigit():
                self.tokens.append(self.read_number())
            elif char in ['"', "'"]:
                self.tokens.append(self.read_string())
            elif char.isalpha() or char == '_':
                self.tokens.append(self.read_identifier())
            elif char in self.operators:
                self.tokens.append(self.read_operator())
            elif char in self.punctuation:
                self.tokens.append(Token(self.punctuation[char], char, self.line, self.column))
                self.advance()
            else:
                # Unknown character, skip it
                self.advance()
        
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens
