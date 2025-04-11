class Grammar:
    def __init__(self, VN, VT, P, S):
        self.VN = VN
        self.VT = VT
        self.P = P
        self.S = S

    def classify(self):
        is_regular = True
        is_context_free = True
        is_context_sensitive = True

        for lhs, rhs_list in self.P.items():
            for rhs in rhs_list:
                if not (len(lhs) == 1 and lhs.isupper() and 
                        (rhs.islower() or (len(rhs) == 2 and rhs[0].islower() and rhs[1].isupper()))):
                    is_regular = False

                if not (len(lhs) == 1 and lhs.isupper()):
                    is_context_free = False

                if len(lhs) > len(rhs):
                    is_context_sensitive = False

        if is_regular:
            return "Type 3 (Regular)"
        elif is_context_free:
            return "Type 2 (Context-Free)"
        elif is_context_sensitive:
            return "Type 1 (Context-Sensitive)"
        else:
            return "Type 0 (Recursively Enumerable)"

grammars = [
    {
        "VN": {"S", "A"},
        "VT": {"a", "b"},
        "P": {
            "S": ["aA", "b"],
            "A": ["a", "bS"]
        },
        "S": "S"
    },
    {
        "VN": {"S", "A", "B"},
        "VT": {"a", "b"},
        "P": {
            "S": ["AB", "a"],
            "A": ["aA", "b"],
            "B": ["bB", "a"]
        },
        "S": "S"
    },
    {
        "VN": {"S", "A", "B"},
        "VT": {"a", "b"},
        "P": {
            "S": ["AB"],
            "A": ["aA", "a"],
            "AB": ["BA"],
            "B": ["bB", "b"]
        },
        "S": "S"
    },
    {
        "VN": {"S", "A", "B", "C"},
        "VT": {"a", "b", "c"},
        "P": {
            "S": ["AB", "bC"],
            "A": ["aA", "ε"],
            "B": ["SB", "b"],
            "BC": ["C"],
            "C": ["c", "ACB"]
        },
        "S": "S"
    }
]

for grammar_data in grammars:
    grammar = Grammar(grammar_data["VN"], grammar_data["VT"], grammar_data["P"], grammar_data["S"])
    print(grammar.classify())
