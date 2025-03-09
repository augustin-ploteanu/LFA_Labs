# Determinism in Finite Automata. Conversion from NDFA 2 DFA. Chomsky Hierarchy.

### Course: Formal Languages & Finite Automata
### Author: Augustin Ploteanu

----

## Theory
A formal language is a set of strings formed from a finite alphabet, through by specific syntactic rules. These languages can be classified into different types based on their expressive power, in this laboratory work a language of type 3 is used, also called regualr grammar. Regular languages, the simplest among them, can be recognised using finite automata. A finite automaton is a mathematical model used to process regular languages through state transitions. It consists of a finite set of states, an input alphabet, a transition function, a start state, and a set of accepting states.

A finite automaton is a mathematical model used to recognise regular languages. It consists of a finite set of states, a set of input symbols (alphabet), a transition function that determines state changes based on input, an initial state, and a set of accepting states. Finite automata can be categorised into deterministic finite automata (DFA) and non-deterministic finite automata (NDFA). A DFA has exactly one transition per symbol for each state, ensuring a unique computation path for any input string. In contrast, an NDFA allows multiple possible transitions for the same symbol from a given state, leading to multiple computation paths. Despite this difference, both models have the same expressive power since every NDFA can be converted into an equivalent DFA.

Grammars provide a rule-based mechanism to define formal languages and are composed of non-terminal symbols, terminal symbols, production rules, and a start symbol. Regular grammars, which correspond to regular languages, can be classified as either right-linear or left-linear depending on the placement of non-terminals in production rules. Context-free grammars (CFGs), which define context-free languages, allow production rules where the left-hand side contains only a single non-terminal, making them suitable for defining programming language syntax and recursive structures.

The conversion between finite automata and regular grammars establishes the equivalence of regular languages in different formal representations. A finite automaton can be transformed into a regular grammar by mapping each state to a non-terminal and defining production rules based on state transitions. Conversely, a regular grammar can be converted into a finite automaton by constructing states corresponding to non-terminals and creating transitions based on production rules. These transformations are essential in lexical analysis, text processing, and compiler design, allowing integration between formal language representations and computational models.

## Objectives:

* Provide a function in the grammar type/class that could classify the grammar based on Chomsky hierarchy.

* Implement conversion of a finite automaton to a regular grammar.

* Determine whether the FA is deterministic or non-deterministic.

* Implement some functionality that would convert an NDFA to a DFA.

## Implementation description

The classify function determines the classification of a given grammar based on the Chomsky hierarchy, which consists of regular (Type 3), context-free (Type 2), context-sensitive (Type 1), and recursively enumerable (Type 0) grammars. It initializes three boolean flags—is_regular, is_context_free, and is_context_sensitive—all set to True, then iterates through the production rules of the grammar. To check if the grammar is regular (Type 3), it verifies that each left-hand side (LHS) consists of a single non-terminal and that the right-hand side (RHS) either contains only terminals or follows a right-linear form (one terminal followed by a non-terminal). If any rule violates this structure, the grammar is not regular. Next, it checks for context-free grammar (Type 2) by ensuring that every LHS consists of a single non-terminal; otherwise, it is not context-free. For context-sensitive grammar (Type 1), it confirms that the LHS is not longer than the RHS in every rule, since context-sensitive grammars must be non-contracting. Finally, the function classifies the grammar based on the most restrictive type it satisfies, returning its corresponding label according to the Chomsky hierarchy.

```
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
```

The isDeterministic function checks whether a finite automaton is deterministic (DFA) or non-deterministic (NDFA) based on its transition function. It iterates through the automaton’s transition dictionary, where each state maps to a set of transitions for input symbols. For each state, it examines whether multiple transitions exist for the same input symbol. If any symbol leads to more than one possible next state, the function returns False, indicating that the automaton is non-deterministic. If no such cases are found, it returns True, confirming that the automaton is deterministic.

```
def isDeterministic(self):
        for state, transitions in self.delta.items():
            for symbol in transitions:
                if len(transitions[symbol]) > 1:
                    return False
        return True
```

The convertToGrammar function transforms a finite automaton into an equivalent regular grammar, demonstrating the equivalence between regular languages and finite-state machines. It first assigns each state in the automaton a corresponding non-terminal symbol using uppercase letters (A, B, C, ...). The function then iterates through the transition function, converting each state transition. If a state has multiple transitions, the rules are appended to the respective non-terminal's production list. Additionally, for final states, an ε-production (A → ε) is added to indicate that the automaton can accept a string at that point. The function returns the set of non-terminals, the set of terminals (alphabet), the constructed production rules, and the start symbol.

```
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
```

The ndfaToDfa function converts a non-deterministic finite automaton (NDFA) into an equivalent deterministic finite automaton (DFA) using the subset construction (powerset) algorithm. It begins by treating the initial state of the NDFA as a set of states (a singleton set containing the start state) and assigns it the first DFA state (A). It maintains a mapping between these sets of NDFA states and newly created DFA states. The function then processes each unprocessed DFA state, iterating through the input alphabet to compute the set of reachable NDFA states for each symbol. If a new set of states is encountered, it is assigned a new DFA state label and added to the processing queue. The function also determines final states in the DFA by checking if any set of states contains an original NDFA final state. The resulting DFA consists of a set of states, a transition table mapping deterministic transitions, and a set of final states.

```
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
```

## Conclusions / Screenshots / Results

Output:
```
Type 3 (Regular)
The FA is deterministic: False
Non-terminals: {'A', 'C', 'B'}
Grammar rules: {'A': ['aA', 'aB', 'bA'], 'B': ['bC', 'aA'], 'C': ['bC', 'ε']}
Type 3 (Regular)
States: ['A', 'B', 'C']
Transitions: {'A': {'b': 'A', 'a': 'B'}, 'B': {'b': 'C', 'a': 'B'}, 'C': {'b': 'C', 'a': 'B'}}
Final States: {'C'}
```

In conclusion, have been developed skills through the practical implementation of formal language theory by integrating grammars and finite automata in Python. It showcases the classification of grammars, the conversion between finite automata and regular grammars, and the transformation of non-deterministic automata into deterministic automata.

## References
Cojuhari Irina, Duca Ludmila, Fiodorov Ion, (2022) *Formal Languages and Finite Automata Guide for practical lessons*