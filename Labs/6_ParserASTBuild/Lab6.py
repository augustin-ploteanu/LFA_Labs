import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Union, Optional

class TokenType(Enum):
    FLOAT = auto()
    NUMBER = auto()
    CONSTANT = auto()
    TRIG = auto()
    LOG = auto()
    IDENTIFIER = auto()
    OPERATOR = auto()
    ABS = auto()
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()
    NEWLINE = auto()
    SKIP = auto()
    MISMATCH = auto()

@dataclass
class Token:
    type: TokenType
    value: Union[str, float, int]
    position: int

TOKEN_SPECIFICATION = [
    (TokenType.FLOAT, r'\d+\.\d+'),
    (TokenType.NUMBER, r'\d+'),
    (TokenType.CONSTANT, r'\b(pi|e)\b'),
    (TokenType.TRIG, r'\b(sin|cos|tan|csc|sec|cot)\b'),
    (TokenType.LOG, r'\b(log|ln|sqrt)\b'),
    (TokenType.IDENTIFIER, r'[a-zA-Z_]\w*'),
    (TokenType.OPERATOR, r'[\+\-\*/\^=]'),
    (TokenType.ABS, r'\|'),
    (TokenType.LPAREN, r'\('),
    (TokenType.RPAREN, r'\)'),
    (TokenType.COMMA, r','),
    (TokenType.NEWLINE, r'\n'),
    (TokenType.SKIP, r'[ \t]+'),
    (TokenType.MISMATCH, r'.'),
]

TOKEN_REGEX = '|'.join(f'(?P<{tok.name}>{pattern})' for tok, pattern in TOKEN_SPECIFICATION)

def tokenize(code: str) -> List[Token]:
    tokens = []
    i = 0
    while i < len(code):
        match = re.match(TOKEN_REGEX, code[i:])
        if not match:
            raise SyntaxError(f"Unexpected character {code[i]} at position {i}")
        kind = TokenType[match.lastgroup]
        value = match.group()
        if kind == TokenType.SKIP or kind == TokenType.NEWLINE:
            i += len(value)
            continue
        elif kind == TokenType.MISMATCH:
            raise SyntaxError(f"Unexpected character {value} at position {i}")
        elif kind == TokenType.FLOAT:
            value = float(value)
        elif kind == TokenType.NUMBER:
            value = int(value)
        elif kind == TokenType.CONSTANT:
            value = 3.141592653589793 if value == 'pi' else 2.718281828459045
        tokens.append(Token(kind, value, i))
        i += len(match.group())
    return tokens

@dataclass
class ASTNode:
    pass

@dataclass
class Number(ASTNode):
    value: Union[int, float]

@dataclass
class Variable(ASTNode):
    name: str

@dataclass
class Constant(ASTNode):
    value: float

@dataclass
class UnaryOp(ASTNode):
    op: str
    operand: ASTNode

@dataclass
class BinaryOp(ASTNode):
    left: ASTNode
    op: str
    right: ASTNode

@dataclass
class FunctionCall(ASTNode):
    name: str
    argument: ASTNode

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def current(self) -> Optional[Token]:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected_type: TokenType = None, expected_value: str = None) -> Token:
        token = self.current()
        if token is None:
            raise SyntaxError("Unexpected end of input")
        if expected_type and token.type != expected_type:
            raise SyntaxError(f"Expected {expected_type.name} but got {token.type.name}")
        if expected_value and token.value != expected_value:
            raise SyntaxError(f"Expected '{expected_value}' but got '{token.value}'")
        self.pos += 1
        return token

    def parse(self) -> ASTNode:
        return self.expression()

    def expression(self, precedence=0) -> ASTNode:
        node = self.primary()

        while self.current() and self.current().type == TokenType.OPERATOR:
            op = self.current().value
            op_precedence = self.get_precedence(op)
            if op_precedence < precedence:
                break
            self.consume(TokenType.OPERATOR)
            right = self.expression(op_precedence + 1)
            node = BinaryOp(left=node, op=op, right=right)
        return node

    def get_precedence(self, op: str) -> int:
        precedences = {'=': 1, '+': 2, '-': 2, '*': 3, '/': 3, '^': 4}
        return precedences.get(op, 0)

    def primary(self) -> ASTNode:
        token = self.current()

        if token.type == TokenType.OPERATOR and token.value == '-':
            self.consume(TokenType.OPERATOR)
            operand = self.primary()
            return UnaryOp(op='-', operand=operand)

        if token.type == TokenType.ABS:
            self.consume(TokenType.ABS)
            expr = self.expression()
            self.consume(TokenType.ABS)
            return UnaryOp(op='abs', operand=expr)

        if token.type == TokenType.LPAREN:
            self.consume(TokenType.LPAREN)
            expr = self.expression()
            self.consume(TokenType.RPAREN)
            return expr

        if token.type in {TokenType.TRIG, TokenType.LOG}:
            name = token.value
            self.consume()
            self.consume(TokenType.LPAREN)
            arg = self.expression()
            self.consume(TokenType.RPAREN)
            return FunctionCall(name=name, argument=arg)

        if token.type == TokenType.CONSTANT:
            self.consume()
            return Constant(value=token.value)

        if token.type == TokenType.FLOAT or token.type == TokenType.NUMBER:
            self.consume()
            return Number(value=token.value)

        if token.type == TokenType.IDENTIFIER:
            self.consume()
            return Variable(name=token.value)

        raise SyntaxError(f"Unexpected token {token.value} at position {token.position}")

def print_ast(node: ASTNode, indent: int = 0):
    prefix = '|   ' * indent + '|─' if indent > 0 else ''
    
    if isinstance(node, Number):
        print(f"{prefix}Number: {node.value}")
    elif isinstance(node, Constant):
        print(f"{prefix}Constant: {node.value}")
    elif isinstance(node, Variable):
        print(f"{prefix}Variable: {node.name}")
    elif isinstance(node, UnaryOp):
        print(f"{prefix}Unary Operation: {node.op}")
        print_ast(node.operand, indent + 1)
    elif isinstance(node, BinaryOp):
        print(f"{prefix}Binary Operation: {node.op}")
        print_ast(node.left, indent + 1)
        print_ast(node.right, indent + 1)
    elif isinstance(node, FunctionCall):
        print(f"{prefix}Function Call: {node.name}")
        print_ast(node.argument, indent + 1)
    else:
        print(f"{prefix}Unknown Node")

code = "2 * 4 + 3 - x"
tokens = tokenize(code)
parser = Parser(tokens)
ast = parser.parse()

print("Abstract Syntax Tree 1:")
print_ast(ast)

print("\n")
code = "x = |sin (pi / 2) + log (100)| + ln (e) + 2.1"
tokens = tokenize(code)
parser = Parser(tokens)
ast = parser.parse()

print("Abstract Syntax Tree 2:")
print_ast(ast)