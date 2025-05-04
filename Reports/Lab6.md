# Parser & Building an Abstract Syntax Tree

### Course: Formal Languages & Finite Automata
### Author: Augustin Ploteanu

----

## Theory
A parser is a component in a compiler or interpreter that takes a sequence of tokens—typically produced by a lexer—and organizes them according to the grammatical structure of the language. This phase is known as syntactic analysis. The parser ensures that the input conforms to the syntax rules and identifies hierarchical relationships between language constructs. There are different parsing strategies, such as top-down and bottom-up each with advantages depending on the complexity of the grammar and the desired features of the parser. If the input violates the syntax, the parser generates appropriate errors, helping developers identify mistakes in their code or expressions.

During the parsing process, the parser constructs an Abstract Syntax Tree (AST), which is a simplified, tree-like representation of the syntactic structure of the source code. Each node in the AST represents a language construct—such as operations, variables, constants, or function calls—without necessarily preserving every syntactic detail. The AST abstracts away the exact formatting of the code and focuses instead on its logical structure. This makes it easier for later stages of interpretation, optimization, or code generation to analyze and manipulate the program.

## Objectives:

*Get familiar with parsing, what it is and how it can be programmed.
*Get familiar with the concept of AST.
*Have a type TokenType (like an enum) that can be used in the lexical analysis to categorize the tokens.
*Use regular expressions to identify the type of the token.
*Implement the necessary data structures for an AST that could be used for the text you have processed in the 3rd lab work.
*Implement a simple parser program that could extract the syntactic information from the input text.

## Implementation description

The tokenize function performs lexical analysis by converting a raw input string (code) into a list of Token objects, each representing a meaningful unit such as a number, operator, function name, or identifier. It uses a regular expression (TOKEN_REGEX) to match patterns defined for each token type and processes the input character by character. If the matched token is whitespace or a newline, it is skipped; if an unexpected or invalid character is encountered, a SyntaxError is raised. For recognized tokens, the function converts their values appropriately—for example, strings to floats, integers, or mathematical constants like π and e—and records their position in the input. The result is a structured list of tokens that can be passed to a parser for further syntactic analysis.

```python
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
```

The Parser class implements a recursive descent parser that analyzes a list of tokens and builds an Abstract Syntax Tree (AST) representing the syntactic structure of an expression. It maintains the current parsing position with self.pos and provides utility methods like current() to retrieve the current token and consume() to advance through the token stream while enforcing expected types or values. The core method parse() initiates the parsing by calling expression(), which respects operator precedence using a precedence climbing approach to correctly group binary operations. The primary() method handles atomic expressions like numbers, constants, variables, function calls, parentheses, unary negation, and absolute value. Special tokens like trigonometric and logarithmic functions are processed as FunctionCall nodes, while arithmetic expressions form BinaryOp and UnaryOp nodes.

```python
class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens, self.pos = tokens, 0

    def current(self) -> Optional[Token]:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected_type=None, expected_value=None) -> Token:
        token = self.current()
        if not token:
            raise SyntaxError("Unexpected end of input")
        if expected_type and token.type != expected_type:
            raise SyntaxError(f"Expected {expected_type.name}, got {token.type.name}")
        if expected_value and token.value != expected_value:
            raise SyntaxError(f"Expected '{expected_value}', got '{token.value}'")
        self.pos += 1
        return token

    def parse(self) -> ASTNode:
        return self.expression()

    def expression(self, precedence=0) -> ASTNode:
        node = self.primary()
        while self.current() and self.current().type == TokenType.OPERATOR:
            op = self.current().value
            if self.get_precedence(op) < precedence:
                break
            self.consume(TokenType.OPERATOR)
            right = self.expression(self.get_precedence(op) + 1)
            node = BinaryOp(left=node, op=op, right=right)
        return node

    def get_precedence(self, op: str) -> int:
        return {'=': 1, '+': 2, '-': 2, '*': 3, '/': 3, '^': 4}.get(op, 0)

    def primary(self) -> ASTNode:
        tok = self.current()

        if tok.type == TokenType.OPERATOR and tok.value == '-':
            self.consume(); return UnaryOp('-', self.primary())
        if tok.type == TokenType.ABS:
            self.consume(); expr = self.expression(); self.consume(TokenType.ABS)
            return UnaryOp('abs', expr)
        if tok.type == TokenType.LPAREN:
            self.consume(); expr = self.expression(); self.consume(TokenType.RPAREN)
            return expr
        if tok.type in {TokenType.TRIG, TokenType.LOG}:
            name = tok.value; self.consume(); self.consume(TokenType.LPAREN)
            arg = self.expression(); self.consume(TokenType.RPAREN)
            return FunctionCall(name, arg)
        if tok.type == TokenType.CONSTANT:
            self.consume(); return Constant(tok.value)
        if tok.type in {TokenType.FLOAT, TokenType.NUMBER}:
            self.consume(); return Number(tok.value)
        if tok.type == TokenType.IDENTIFIER:
            self.consume(); return Variable(tok.value)

        raise SyntaxError(f"Unexpected token {tok.value} at position {tok.position}")
```

The eliminate_inaccessible_symbols function removes symbols (both non-terminals and terminals) that cannot be reached from the start symbol in a context-free grammar. It begins by initializing a set of reachable symbols, starting with the start symbol itself, and then performs a traversal over the grammar's productions to collect all symbols that can be reached either directly or indirectly from the start symbol. This is done by iteratively exploring the right-hand sides of reachable productions and adding any variables or terminals found to the processing set. After identifying all reachable symbols, the function filters out any non-terminals and associated productions that were not reached, effectively pruning the grammar of unused components that do not contribute to generating strings from the start symbol.

```python
def eliminate_inaccessible_symbols(self):
        reachable = set()
        to_process = {self.start_symbol}

        while to_process:
            symbol = to_process.pop()
            if symbol in reachable:
                continue
            reachable.add(symbol)
            for rule in self.productions.get(symbol, []):
                for sym in rule:
                    if sym in self.variables or sym in self.terminals:
                        to_process.add(sym)

        self.variables = self.variables & reachable
        self.productions = {
            var: rules for var, rules in self.productions.items() if var in reachable
        }
```

The print_ast function recursively traverses and displays an Abstract Syntax Tree (AST) in a human-readable, indented format that visually represents the tree structure. It prints each node with a prefix indicating its depth in the tree (indent), using vertical bars and dashes to suggest hierarchy. Depending on the node type—such as Number, Constant, Variable, UnaryOp, BinaryOp, or FunctionCall—it prints a descriptive label along with the relevant value or operator. For compound nodes like UnaryOp, BinaryOp, and FunctionCall, the function recursively prints their child nodes at a deeper indentation level, making the logical structure of the expression easy to understand visually.

```python
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
```

## Conclusions / Screenshots / Results

Input:
```
"2 * 4 + 3 - x"
"x = |sin (pi / 2) + log (100)| + ln (e) + 2.1"
```

Output:
```
Abstract Syntax Tree 1:
Binary Operation: -
|   |─Binary Operation: +
|   |   |─Binary Operation: *
|   |   |   |─Number: 2
|   |   |   |─Number: 4
|   |   |─Number: 3
|   |─Variable: x

Abstract Syntax Tree 2:
Binary Operation: =
|   |─Variable: x
|   |─Binary Operation: +
|   |   |─Binary Operation: +
|   |   |   |─Unary Operation: abs
|   |   |   |   |─Binary Operation: +
|   |   |   |   |   |─Function Call: sin
|   |   |   |   |   |   |─Binary Operation: /
|   |   |   |   |   |   |   |─Constant: 3.141592653589793
|   |   |   |   |   |   |   |─Number: 2
|   |   |   |   |   |─Function Call: log
|   |   |   |   |   |   |─Number: 100
|   |   |   |─Function Call: ln
|   |   |   |   |─Constant: 2.718281828459045
|   |   |─Number: 2.1
```

In conclusion, the implementation of the parser and abstract syntax tree builder provides a structured approach to syntactic analysis for mathematical expressions. The tokenizer classifies input using regular expressions, while the parser constructs a hierarchical AST that reflects the grammatical structure of the expression with respect to operator precedence and function semantics. The use of clearly defined AST node types enables easy traversal, visualization, and further processing, such as interpretation or code generation. Together, these components form a foundational system for analyzing and understanding the structure of input expressions in a reliable and extensible way.

## References
Cojuhari Irina, Duca Ludmila, Fiodorov Ion, (2022) *Formal Languages and Finite Automata Guide for practical lessons*

Wikipedia *Parsing*

Wikipedia *Abstract Syntax Tree*