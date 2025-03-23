# Lexer & Scanner

### Course: Formal Languages & Finite Automata
### Author: Augustin Ploteanu

----

## Theory
Lexical analysis is the first phase of the compilation process, responsible for breaking down a sequence of characters from a source code file into meaningful units known as tokens. Tokens represent the smallest units of meaning in a programming language, such as keywords, identifiers, operators, literals, and punctuation symbols. The lexical analyzer, or lexer, reads the source code character by character, matches patterns using regular expressions, and categorizes the recognized strings according to predefined rules. Once recognized, tokens are typically classified with a type and value, which can later be processed by other components of the compiler or interpreter. Additionally, lexical analysis is responsible for eliminating unnecessary elements like whitespace and comments, making the source code easier to process for the subsequent phases of compilation.

A well-designed lexical analyzer also performs error detection and reporting, identifying invalid tokens and providing feedback to the user for correction. For instance, the lexer may detect unrecognized characters, invalid numbers, or improperly formed operators. While lexical analysis is primarily concerned with breaking down the input into tokens, it often performs some basic error handling and checking, such as ensuring that certain tokens are used correctly in context (e.g., ensuring that function names are followed by parentheses). Modern lexers are efficient and fast, designed to process large amounts of text quickly. They serve as the foundation of many programming language processors, including compilers, interpreters, and even text processing tools like formatters and syntax highlighters.

## Objectives:

* Get familiar with the inner workings of a lexer/scanner/tokenizer.

* Implement a sample lexer and show how it works.

## Implementation description

The TOKEN_SPECIFICATION list defines the various tokens that the lexer will recognise from the input code. Each entry in the list is a tuple consisting of a token name and a corresponding regular expression pattern. Tokens include numbers (FLOAT, NUMBER), functions (TRIG, SQRT, LOG, LN), constants (PI, E), arithmetic operators (PLUS, MINUS, TIMES, DIVIDE, POWER), parentheses (LPAREN, RPAREN), assignment (ASSIGN), identifiers (IDENTIFIER), and special symbols like absolute value (ABS) and commas (COMMA). The MISMATCH pattern is used as a fallback to catch invalid characters. The lexer uses these patterns to categorize different parts of the input code.

```python
TOKEN_SPECIFICATION = [
    ('FLOAT', r'\d+\.\d+'),
    ('NUMBER', r'\d+'),
    ('TRIG', r'\b(sin|cos|tan|csc|sec|cot)\b'),
    ('SQRT', r'\bsqrt\b'),
    ('LOG', r'\blog\b'),
    ('LN', r'\bln\b'),
    ('PI', r'\bpi\b'),
    ('E', r'\be\b'),
    ('ABS', r'\|'),
    ('POWER', r'\^'),
    ('IDENTIFIER', r'[a-zA-Z_]\w*'),
    ('ASSIGN', r'='),
    ('PLUS', r'\+'),
    ('MINUS', r'-'),
    ('TIMES', r'\*'),
    ('DIVIDE', r'/'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('COMMA', r','),
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t]+'),
    ('MISMATCH', r'.'),
]
```

This section creates a combined regular expression pattern TOKEN_REGEX using all the defined tokens in TOKEN_SPECIFICATION. The pattern uses named groups, allowing the lexer to identify the matched token type. Additionally, the OPERATORS set is defined to keep track of arithmetic operators that should not appear consecutively, and the FUNCTIONS set specifies functions (sin, sqrt, log, ln) that require parentheses to be valid. This structure prepares the lexer to accurately identify tokens and detect errors related to consecutive operators or invalid function usage.

```python
TOKEN_REGEX = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPECIFICATION)
OPERATORS = {'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'POWER'}
FUNCTIONS = {'TRIG', 'SQRT', 'LOG', 'LN'}
```

The lexer() function is responsible for processing the input code and categorizing it into tokens. It initializes an empty list tokens to store valid tokens, an empty list errors to collect error messages, and a variable previous_kind to track the last recognized token type.

The function uses a while loop to iterate over the code string. It tries to match the code against TOKEN_REGEX starting from the current position (i). If a match is found, the lexer identifies the token type (kind) and value (value) and converts numeric values to appropriate data types (float for FLOAT and int for NUMBER). It also assigns numerical values to constants like PI and E. Errors such as incorrect comma usage or invalid characters are detected and recorded in the errors list. If the lexer fails to match any token, it reports an unexpected character error.

The lexer checks for consecutive operators by comparing the current token type with the previous one. If two operators are found in succession, an error message is recorded. It also ensures that functions like sin, log, sqrt, and ln are followed by parentheses. If parentheses are missing or empty, appropriate errors are generated.

```python
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
        elif kind == 'PI':
            value = 3.141592653589793
        elif kind == 'E':
            value = 2.718281828459045
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
```

## Conclusions / Screenshots / Results

Input:
```
x = |sin(pi/2) + log(100)| + ln(e) + 2,1 + - 7 + sqrt(4) + tan()
```

Output:
```
('IDENTIFIER', 'x')
('ASSIGN', '=')
('ABS', '|')
('TRIG', 'sin')
('LPAREN', '(')
('PI', 3.141592653589793)
('DIVIDE', '/')
('NUMBER', 2)
('RPAREN', ')')
('PLUS', '+')
('LOG', 'log')
('LPAREN', '(')
('NUMBER', 100)
('RPAREN', ')')
('ABS', '|')
('PLUS', '+')
('LN', 'ln')
('LPAREN', '(')
('E', 2.718281828459045)
('RPAREN', ')')
('PLUS', '+')
('NUMBER', 2)
('NUMBER', 1)
('PLUS', '+')
('MINUS', '-')
('NUMBER', 7)
('PLUS', '+')
('SQRT', 'sqrt')
('LPAREN', '(')
('NUMBER', 4)
('RPAREN', ')')
('PLUS', '+')
('TRIG', 'tan')
('LPAREN', '(')
('RPAREN', ')')
Invalid use of ','. Use '.' for floating-point numbers at position 38
Consecutive operator error: '+-' at position 43
Empty parentheses or missing ')' after 'tan' at position 59
```

In conclusion, the implementation of the lexer breaks down mathematical expressions into meaningful tokens while ensuring proper error handling for various invalid scenarios. It identifies functions, constants, numbers, operators, and symbols, and ensures that functions like sin, log, sqrt, and ln are always followed by valid parentheses containing valid expressions. Additionally, it detects consecutive operator errors, improper floating-point notation using commas, and reports them with clear messages.

## References
Cojuhari Irina, Duca Ludmila, Fiodorov Ion, (2022) *Formal Languages and Finite Automata Guide for practical lessons*

LLVM *Kaleidoscope: Kaleidoscope Introduction and the Lexer*

Wikipedia *Lexical analysis*