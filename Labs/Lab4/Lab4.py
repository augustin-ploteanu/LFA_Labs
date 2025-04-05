import random

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

regex = "O(P|Q|R)+2(3|4)"
print(f"Regex: {regex}")
for _ in range(10):
    print(generate(parse_expression(regex)))

regex = "A*B(C|D|E)F(G|H|I)^2"
print(f"\nRegex: {regex}")
for _ in range(10):
    print(generate(parse_expression(regex)))

regex = "J+K(L|M|N)*0?(P|Q)^3"
print(f"\nRegex: {regex}")
for _ in range(10):
    print(generate(parse_expression(regex)))