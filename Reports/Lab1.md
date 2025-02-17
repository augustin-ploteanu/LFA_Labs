# Intro to formal languages. Regular grammars. Finite Automata.

### Course: Formal Languages & Finite Automata
### Author: Augustin Ploteanu

----

## Theory
A formal language is a set of strings formed from a finite alphabet, through by specific syntactic rules. These languages can be classified into different types based on their expressive power, in this laboratory work a language of type 3 is used, also called regualr grammar. Regular languages, the simplest among them, can be recognised using finite automata. A finite automaton is a mathematical model used to process regular languages through state transitions. It consists of a finite set of states, an input alphabet, a transition function, a start state, and a set of accepting states.


## Objectives:

* Implement a type/class for the grammar;

* Function that would generate 5 valid strings from the language expressed by the given grammar;

* Functionality that would convert and object of type Grammar to one of type Finite Automaton;

* Method that checks if an input string can be obtained via the state transition from the Finite Automaton.


## Implementation description

The generateString function generates a random string from the grammar by starting with the initial symbol S and repeatedly replacing the leftmost non-terminal with a randomly chosen production rule until only terminal symbols remain. It iterates through the string, identifying non-terminals, and replaces them one by one using the production rules defined in P. Once no non-terminals are left, the generated string is printed.

```
def generateString(self):
        gen_string = self.S
        while gen_string[-1] in self.VN:
            for i, symbol in enumerate(gen_string):
                if symbol in self.VN:
                    repl = random.choice(self.P[symbol])
                    gen_string = gen_string[:i] + repl + gen_string[i+1:]
                    break
        print(gen_string)
```

The toFiniteAutomaton function converts a grammar into an equivalent finite automaton by defining its states (Q), input alphabet (sigma), transition function (delta), start state (q0), and accepting states (F). It iterates through the grammar’s production rules and maps transitions from non-terminals to either terminal symbols (leading to the accepting state) or other non-terminals. Finally, it returns a FiniteAutomaton object initialized with these components.

```
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
```

The stringBelongToLanguage function checks whether a given input_string is accepted by the finite automaton by simulating state transitions. It starts from the initial state (q0) and processes each symbol, updating the current state based on the transition function (delta). If a valid transition does not exist, it returns False; otherwise, after processing all symbols, it returns True if the final state is in the set of accepting states (F).

```
def stringBelongToLanguage(self, input_string):
        current_state = self.q0
        for symbol in input_string:
            if (current_state, symbol) in self.delta:
                current_state = self.delta[(current_state, symbol)]
            else:
                return False
        return current_state in self.F
```


## Conclusions / Screenshots / Results

Output of generating 5 strings and checking if the following strings: a, aab, c, aac, abac; can be obtained via the state transition from the finite automaton:
```
ababac
aac
aabbbbbabababbaaabac
aac
ababaaabac

False
False
False
True
True
```

In conclusion, have been developed skills in using grammar and finite automaton in the Python programming language.

## References
Cojuhari Irina, Duca Ludmila, Fiodorov Ion, (2022) *Formal Languages and Finite Automata Guide for practical lessons*