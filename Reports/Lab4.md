# Regular expressions

### Course: Formal Languages & Finite Automata
### Author: Augustin Ploteanu

----

## Theory
Regular expressions (regex) are symbolic patterns used to describe sets of strings. They provide a concise and flexible way to search, match, and manipulate text based on specific patterns. At their core, regular expressions are built from literal characters combined with metacharacters such as * (zero or more), + (one or more), ? (zero or one), and | (alternation). Parentheses () are used to group expressions, while character classes like [a-z] define sets of possible characters. These components form a powerful syntax for defining complex text-matching rules in programming, search utilities, and data validation.

The idea of regular expressions comes from computer science, where they are used to describe patterns in text using a set of rules. These patterns match what are called "regular languages," which can be processed by simple machines called finite automata. This means regular expressions can be used to check and find patterns quickly. In practice, many programming languages and tools use regular expressions to search and manage text. Some versions also add extra features like checking ahead in the text or remembering parts of a match, which makes them more powerful but sometimes more complex.

## Objectives:

* Write a code that will generate valid combinations of symbols conform given regular expressions (examples will be shown). Be careful that idea is to interpret the given regular expressions dinamycally, not to hardcode the way it will generate valid strings. You give a set of regexes as input and get valid word as an output.

* In case you have an example, where symbol may be written undefined number of times, take a limit of 5 times (to evade generation of extremely long combinations).

## Implementation description

The parse_expression function takes a regular expression string and converts it into a nested tree structure that represents its components and operators. It uses a helper function parse_group to recursively process characters in the expression, handling grouping with parentheses, alternation with |, repetition operators like *, +, ?, and power-based repetition using ^ followed by a number. As it parses, it builds a list of tokens or subgroups that reflect the order and hierarchy of the expression. The final result is a structured representation (parse tree) that can later be used for evaluation or string generation based on the original regex pattern.

```python
def parse_expression(regex):
    def parse_group(i):
        result = []
        while i < len(regex):
            c = regex[i]
            if c == ')':
                return result, i
            elif c == '(':
                group, i = parse_group(i + 1)
                result.append(group)
            elif c == '|':
                left = result
                right, i = parse_group(i + 1)
                return [['|', left, right]], i
            elif c in '*+?':
                prev = result.pop()
                result.append([c, prev])
            elif c == '^':
                prev = result.pop()
                j = i + 1
                power = ''
                while j < len(regex) and regex[j].isdigit():
                    power += regex[j]
                    j += 1
                power_val = int(power)
                result.append(['^', prev, power_val])
                i = j - 1
            else:
                result.append(c)
            i += 1
        return result, i

    tree, _ = parse_group(0)
    return tree
```

The generate function takes a parse tree (created from a regular expression) and produces a random string that matches the pattern described by that tree. It handles different regex operations by checking the type of each node: alternation (|) randomly picks one branch, * and + repeat the inner pattern a random number of times, ? includes the pattern optionally, and ^ repeats a pattern a fixed number of times. If the pattern being repeated with ^ is an alternation, it ensures the same choice is used for all repetitions. For plain strings or characters, it returns them directly, and for nested structures, it recursively processes and joins the results.

```python
def generate(tree):
    if isinstance(tree, str):
        return tree
    if isinstance(tree, list):
        if not tree:
            return ''
        if tree[0] == '|':
            return generate(random.choice([tree[1], tree[2]]))
        elif tree[0] == '*':
            return ''.join(generate(tree[1]) for _ in range(random.randint(0, 5)))
        elif tree[0] == '+':
            return ''.join(generate(tree[1]) for _ in range(random.randint(1, 5)))
        elif tree[0] == '?':
            return generate(tree[1]) if random.random() > 0.5 else ''
        elif tree[0] == '^':
            base, count = tree[1], tree[2]
            if isinstance(base, list) and base[0] == '|':
                chosen = random.choice([base[1], base[2]])
                return ''.join(generate(chosen) for _ in range(count))
            else:
                generated = generate(base)
                return generated * count
        else:
            return ''.join(generate(token) for token in tree)
    return ''
```

## Conclusions / Screenshots / Results

Input:
```
O(P|Q|R)+2(3|4)
A*B(C|D|E)F(G|H|I)^2
J+K(L|M|N)*0?(P|Q)^3
```

Output:
```
Regex: O(P|Q|R)+2(3|4)
OPPPR23
OPQPRP24
OPPQP24
OPPQPQ23
ORR23

Regex: A*B(C|D|E)F(G|H|I)^2
AABCFGG
AABEFGG
AAABCFGG
ABCFGG
AABCFHH

Regex: J+K(L|M|N)*0?(P|Q)^3
JJJJKNLQQQ
JJJJKMLNLPPP
JJJKLLLML0PPP
JJKLLLLM0PPP
JJKLLNMNPPP
```

In conclusion, the implementation of the regular expression parser and generator effectively transforms regex patterns into structured parse trees and uses them to generate random strings that match the defined patterns. It supports regex operations such as grouping, alternation, repetition, and fixed-count repetition using the ^ operator. The parser ensures correct interpretation of nested expressions, while the generator respects the structure to produce valid and consistent outputs.

## References
Cojuhari Irina, Duca Ludmila, Fiodorov Ion, (2022) *Formal Languages and Finite Automata Guide for practical lessons*