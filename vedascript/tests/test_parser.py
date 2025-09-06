import pytest
from vedascript.parser.parser import VedaScriptParser
from vedascript.lexer.lexer import VedaScriptLexer

def test_simple_expression():
    code = "5 + 3"
    lexer = VedaScriptLexer(code)
    tokens = lexer.tokenize()
    parser = VedaScriptParser(tokens)
    ast = parser.parse()
    assert ast is not None

def test_variable_declaration():
    code = "var x = 10"
    lexer = VedaScriptLexer(code)
    tokens = lexer.tokenize()
    parser = VedaScriptParser(tokens)
    ast = parser.parse()
    assert ast is not None

def test_function_declaration():
    code = """
    function test() {
        var x = 5
        return x
    }
    """
    lexer = VedaScriptLexer(code)
    tokens = lexer.tokenize()
    parser = VedaScriptParser(tokens)
    ast = parser.parse()
    assert ast is not None
