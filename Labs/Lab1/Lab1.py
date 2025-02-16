import random

class Grammar:
    def __init__(self, VN, VT, P, S):
        self.VN = VN
        self.VT = VT
        self.P = P
        self.S = S

    def generateString(self):
        gen_string = self.S
        while gen_string[-1] in self.VN:
            for i, symbol in enumerate(gen_string):
                if symbol in self.VN:
                    repl = random.choice(self.P[symbol])
                    gen_string = gen_string[:i] + repl + gen_string[i+1:]
                    break
        print(gen_string)

    def toFiniteAutomaton(self):
        Q = self.VN | {"q_accept"}
        sigma = self.VT
        delta = {}
        q0 = self.S
        F = {"q_accept"}

        for non_terminal, productions in self.P.items():
            for production in productions:
                if len(production) == 1 and production in self.VT:
                    delta[(non_terminal, production)] = "q_accept"
                else:
                    delta[(non_terminal, production[0])] = production[1:]

        return FiniteAutomaton(Q, sigma, delta, q0, F)

class FiniteAutomaton:
    def __init__(self, Q, sigma, delta, q0, F):
        self.Q = Q
        self.sigma = sigma
        self.delta = delta
        self.q0 = q0
        self.F = F

    def stringBelongToLanguage(self, input_string):
        current_state = self.q0
        for symbol in input_string:
            if (current_state, symbol) in self.delta:
                current_state = self.delta[(current_state, symbol)]
            else:
                return False
        return current_state in self.F

def main():
    VN = {"S", "B", "C"}
    VT = {"a", "b", "c"}
    P = {
        "S": ["aB"],
        "B": ["aC", "bB"],
        "C": ["bB", "c", "aS"]
    }
    S = "S"

    grammar = Grammar(VN, VT, P, S)
    for i in range(5):
        grammar.generateString()
    fa = grammar.toFiniteAutomaton()
    print(fa.stringBelongToLanguage("a"))
    print(fa.stringBelongToLanguage("aab"))
    print(fa.stringBelongToLanguage("c"))
    print(fa.stringBelongToLanguage("aac"))
    print(fa.stringBelongToLanguage("abac"))

if __name__ == "__main__":
    main()