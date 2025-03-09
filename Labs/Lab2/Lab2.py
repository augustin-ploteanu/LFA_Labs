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

VN = {"S", "B", "C"}
VT = {"a", "b", "c"}
P = {
    "S": ["aB"],
    "B": ["aC", "bB"],
    "C": ["bB", "c", "aS"]
}
S = "S"

grammar = Grammar(VN, VT, P, S)
print(grammar.classify())

class FiniteAutomaton:
    def __init__(self, Q, sigma, delta, q0, F):
        self.Q = Q
        self.sigma = sigma
        self.delta = delta
        self.q0 = q0
        self.F = F

    def isDeterministic(self):
        for state, transitions in self.delta.items():
            for symbol in transitions:
                if len(transitions[symbol]) > 1:
                    return False
        return True

    def convertToGrammar(self):
        state_mapping = {state: chr(65 + i) for i, state in enumerate(sorted(self.Q))}
        grammar_productions = {}

        for state, transitions in self.delta.items():
            for symbol, next_states in transitions.items():
                for next_state in next_states:
                    rule = f"{symbol}{state_mapping[next_state]}"
                    if state_mapping[state] in grammar_productions:
                        grammar_productions[state_mapping[state]].append(rule)
                    else:
                        grammar_productions[state_mapping[state]] = [rule]

        for final_state in self.F:
            if state_mapping[final_state] in grammar_productions:
                grammar_productions[state_mapping[final_state]].append("ε")
            else:
                grammar_productions[state_mapping[final_state]] = ["ε"]

        return set(state_mapping.values()), set(self.sigma), grammar_productions, state_mapping[self.q0]

    def ndfaToDfa(self):
        dfa_states = [frozenset([self.q0])]
        dfa_transitions = {}
        dfa_final_states = set()

        state_map = {frozenset([self.q0]): 'A'}
        unprocessed_states = [frozenset([self.q0])]

        while unprocessed_states:
            current_state = unprocessed_states.pop()
            current_state_name = state_map[current_state]

            for symbol in self.sigma:
                next_state = set()
                for state in current_state:
                    if symbol in self.delta.get(state, {}):
                        next_state.update(self.delta[state].get(symbol, []))

                if next_state:
                    next_state_frozenset = frozenset(next_state)
                    if next_state_frozenset not in state_map:
                        state_map[next_state_frozenset] = chr(65 + len(state_map))
                        unprocessed_states.append(next_state_frozenset)

                    if current_state_name not in dfa_transitions:
                        dfa_transitions[current_state_name] = {}
                    dfa_transitions[current_state_name][symbol] = state_map[next_state_frozenset]

                    if next_state & set(self.F):
                        dfa_final_states.add(state_map[next_state_frozenset])

        return list(state_map.values()), dfa_transitions, dfa_final_states

Q = {"q0", "q1", "q2"}
sigma = {"a", "b"}
F = {"q2"}
delta = {
    "q0": {"a": ["q0", "q1"], "b": ["q0"]},
    "q1": {"b": ["q2"], "a": ["q0"]},
    "q2": {"b": ["q2"]}
}
q0 = "q0"

fa = FiniteAutomaton(Q, sigma, delta, q0, F)

print(f"The FA is deterministic: {fa.isDeterministic()}")
VN, VT, P, S = fa.convertToGrammar()
print(f"Non-terminals: {VN}")
print(f"Grammar rules: {P}")
grammar = Grammar(VN, VT, P, S)
print(grammar.classify())
Q, delta, F = fa.ndfaToDfa()
print(f"States: {Q}")
print(f"Transitions: {delta}")
print(f"Final States: {F}")