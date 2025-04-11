import re

TOKEN_SPECIFICATION = [
    ('FLOAT', r'\d+\.\d+'),
    ('NUMBER', r'\d+'),
    ('CONSTANT', r'\b(pi|e)\b'),
    ('TRIG', r'\b(sin|cos|tan|csc|sec|cot)\b'),
    ('LOG', r'\b(log|ln|sqrt)\b'),
    ('IDENTIFIER', r'[a-zA-Z_]\w*'),
    ('OPERATOR', r'[\+\-\*/\^=]'),
    ('ABS', r'\|'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('COMMA', r','),
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t]+'),
    ('MISMATCH', r'.'),
]

TOKEN_REGEX = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPECIFICATION)
OPERATORS = {'OPERATOR'}
FUNCTIONS = {'TRIG', 'LOG'}

def lexer(code):
    tokens = []
    previous_kind = None
    errors = []
    i = 0 

    while i < len(code):
        match = re.match(TOKEN_REGEX, code[i:])
        if not match:
            errors.append(f"Unexpected character: {code[i]} at position {i}")
            i += 1
            continue

        kind = match.lastgroup
        value = match.group()
        start_index = i
        end_index = i + len(value)
        
        if kind == 'FLOAT':
            value = float(value)
        elif kind == 'NUMBER':
            value = int(value)
        elif kind == 'CONSTANT':
            value = 3.141592653589793 if value == 'pi' else 2.718281828459045
        elif kind == 'COMMA':
            errors.append(f"Invalid use of ','. Use '.' for floating-point numbers at position {start_index}")
            i = end_index
            continue
        elif kind == 'SKIP' or kind == 'NEWLINE':
            i = end_index
            continue
        elif kind == 'MISMATCH':
            errors.append(f"Unexpected character: {value} at position {start_index}")
            i = end_index
            continue
        
        if previous_kind in OPERATORS and kind in OPERATORS:
            errors.append(f"Consecutive operator error: '{tokens[-1][1]}{value}' at position {start_index}")
        
        if kind in FUNCTIONS:
            if i + len(value) >= len(code) or code[end_index] != '(':
                errors.append(f"Missing '(' after '{value}' at position {start_index}")
            else:
                closing_index = code.find(')', end_index)
                if closing_index == -1 or closing_index == end_index + 1:
                    errors.append(f"Empty parentheses or missing ')' after '{value}' at position {start_index}")
        
        tokens.append((kind, value))
        previous_kind = kind
        i = end_index

    for token in tokens:
        print(token)
    
    if errors:
        for error in errors:
            print(error)

code = "x = |sin(pi/2) + log(100)| + ln(e) + 2,1 + - 7 + sqrt(4) + tan()"
lexer(code)