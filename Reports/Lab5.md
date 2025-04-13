# Chomsky Normal Form

### Course: Formal Languages & Finite Automata
### Author: Augustin Ploteanu

----

## Theory
Chomsky Normal Form (CNF) is a standardized way of expressing context-free grammars (CFGs) in which each production rule conforms to one of two specific patterns: either a non-terminal producing exactly two non-terminals (i.e.,A→BC) or a non-terminal producing a single terminal (i.e.,A→a). Optionally, the start symbol may also produce the empty string (ε), but only if ε is part of the original language. This strict structure is especially useful in theoretical computer science and formal language theory because it simplifies parsing algorithms which require grammars to be in CNF to function efficiently.

Converting a CFG to CNF involves a series of transformation steps to simplify and restructure the grammar without changing the language it generates. These steps typically include eliminating ε-productions (rules that produce the empty string), unit productions (rules like A→B), inaccessible symbols (those that cannot be reached from the start symbol), and non-productive symbols (those that do not lead to terminal strings). After these simplifications, the remaining rules are reshaped into the strict CNF format by introducing new variables to break down longer rules and by substituting terminals in mixed rules. This normalization process is crucial in the fields of compiler design, formal verification, and automata theory, as it allows algorithms to operate on grammars in a consistent and predictable way.

## Objectives:

* Learn about Chomsky Normal Form (CNF).
* Get familiar with the approaches of normalizing a grammar.
* Implement a method for normalizing an input grammar by the rules of CNF.
* The implementation needs to be encapsulated in a method with an appropriate signature (also ideally in an appropriate class/type).
* The implemented functionality needs executed and tested.

## Implementation description

The eliminate_epsilon_productions function is responsible for removing ε-productions (rules that derive the empty string) from a context-free grammar, except possibly from the start symbol. It first identifies all nullable variables—those that can derive ε either directly or through a chain of other nullable variables. Once the set of nullable variables is established, the function then generates all possible variants of each production by optionally omitting the nullable symbols, effectively simulating the ε-productions without explicitly including them. This generation of rule variants is delegated to the helper function _generate_nullable_variants, which takes a production rule and the set of nullable symbols, and systematically constructs all combinations of the rule with subsets of the nullable symbols removed. This ensures that the resulting grammar no longer contains ε-productions but still captures the same language.

```python
def eliminate_epsilon_productions(self):
        nullable = set()
        changed = True
        while changed:
            changed = False
            for var, rules in self.productions.items():
                for rule in rules:
                    if all(sym in nullable or sym == 'ε' for sym in rule):
                        if var not in nullable:
                            nullable.add(var)
                            changed = True

        new_productions = {}
        for var in self.productions:
            new_rules = set()
            for rule in self.productions[var]:
                rule_variants = self._generate_nullable_variants(rule, nullable)
                new_rules.update(rule_variants)
            if var != self.start_symbol:
                new_rules.discard(('ε',))
            new_productions[var] = [list(r) for r in new_rules if r]

        self.productions = new_productions

    def _generate_nullable_variants(self, rule: List[str], nullable: Set[str]) -> Set[Tuple[str]]:
        from itertools import combinations
        positions = [i for i, sym in enumerate(rule) if sym in nullable]
        variants = set()
        for i in range(0, len(positions) + 1):
            for subset in combinations(positions, i):
                temp = [sym for idx, sym in enumerate(rule) if idx not in subset]
                if temp:
                    variants.add(tuple(temp))
                else:
                    variants.add(('ε',))
        return variants
```

The eliminate_unit_productions function removes unit productions from a context-free grammar—these are rules where one non-terminal directly produces another non-terminal (e.g., A→B). First, it collects all such unit pairs into a set and then computes the transitive closure of these pairs to account for indirect relationships (e.g., if A→B and B→C, then A→C is also a unit relation). Once all unit pairs are identified, the function builds a new set of productions by copying over all non-unit rules and replacing unit productions by the actual rules of their targets. This effectively inlines the rules of the referenced non-terminal, eliminating the intermediate step. As a result, the updated grammar maintains the same language but without relying on direct non-terminal to non-terminal transitions.

```python
def eliminate_unit_productions(self):
        unit_pairs = set()
        for A in self.variables:
            for rule in self.productions.get(A, []):
                if len(rule) == 1 and rule[0] in self.variables:
                    unit_pairs.add((A, rule[0]))

        changed = True
        while changed:
            changed = False
            new_pairs = set()
            for (A, B) in unit_pairs:
                for (C, D) in unit_pairs:
                    if B == C and (A, D) not in unit_pairs:
                        new_pairs.add((A, D))
                        changed = True
            unit_pairs.update(new_pairs)

        new_productions = {var: [] for var in self.variables}
        for A in self.variables:
            for rule in self.productions.get(A, []):
                if not (len(rule) == 1 and rule[0] in self.variables):
                    new_productions[A].append(rule)

        for (A, B) in unit_pairs:
            for rule in self.productions.get(B, []):
                if not (len(rule) == 1 and rule[0] in self.variables):
                    if rule not in new_productions[A]:
                        new_productions[A].append(rule)

        self.productions = new_productions
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

The eliminate_nonproductive_symbols function removes non-terminals that cannot derive any string composed entirely of terminal symbols, ensuring that the grammar only contains productive symbols. It begins by identifying productive non-terminals—those that directly produce terminal strings or can eventually do so through other productive symbols—using a fixpoint iteration approach. In each iteration, it checks whether a variable can derive a string where all symbols are either terminals or already known to be productive, adding it to the productive set if so. After all productive variables are identified, the function filters out any unproductive variables and their corresponding productions.

```python
def eliminate_nonproductive_symbols(self):
        productive = set()

        changed = True
        while changed:
            changed = False
            for var, rules in self.productions.items():
                if var in productive:
                    continue
                for rule in rules:
                    if all(sym in self.terminals or sym in productive for sym in rule):
                        productive.add(var)
                        changed = True
                        break

        self.variables = self.variables & productive
        new_productions = {}
        for var in productive:
            new_rules = []
            for rule in self.productions.get(var, []):
                if all(sym in self.terminals or sym in productive for sym in rule):
                    new_rules.append(rule)
            new_productions[var] = new_rules

        self.productions = new_productions
```

The to_cnf function transforms a context-free grammar into Chomsky Normal Form (CNF), where each production rule must either produce two non-terminals or a single terminal. It first replaces terminals in longer rules with new non-terminal variables, ensuring that each terminal appears alone in its own rule (e.g., replacing a terminal in a multi-symbol rule like A → aB with A → X1B and X1 → a). This mapping is stored in a dictionary called terminal_map to avoid creating duplicate variables for the same terminal. Next, it recursively breaks down rules with more than two symbols on the right-hand side by introducing new intermediate variables so that each production becomes binary (e.g., transforming A → BCD into A → X1D and X1 → BC). The helper method _get_new_variable generates unique variable names (e.g., X1, X2, ...) to avoid collisions with existing variables. As a result, the grammar is restructured to meet the strict format of CNF while preserving its original language.

```python
def to_cnf(self):
        terminal_map = {}
        new_productions = {}

        for var, rules in self.productions.items():
            new_rules = []
            for rule in rules:
                if len(rule) > 1:
                    new_rule = []
                    for symbol in rule:
                        if symbol in self.terminals:
                            if symbol not in terminal_map:
                                new_var = self._get_new_variable()
                                terminal_map[symbol] = new_var
                                self.variables.add(new_var)
                                new_productions[new_var] = [[symbol]]
                            new_rule.append(terminal_map[symbol])
                        else:
                            new_rule.append(symbol)
                    new_rules.append(new_rule)
                else:
                    new_rules.append(rule)
            new_productions[var] = new_rules

        final_productions = {}
        for var, rules in new_productions.items():
            final_rules = []
            for rule in rules:
                while len(rule) > 2:
                    new_var = self._get_new_variable()
                    self.variables.add(new_var)
                    final_productions[new_var] = [[rule[0], rule[1]]]
                    rule = [new_var] + rule[2:]
                final_rules.append(rule)
            final_productions[var] = final_rules

        self.productions = final_productions

    def _get_new_variable(self) -> str:
        while True:
            candidate = f"X{self.new_var_counter}"
            self.new_var_counter += 1
            if candidate not in self.variables:
                return candidate
```

## Conclusions / Screenshots / Results

Input:
```
variables = {'S', 'A', 'B', 'C', 'E'}
terminals = {'a', 'b'}
productions = {
    'S': [['b', 'A', 'C'], ['B']],
    'A': [['a'], ['a', 'S'], ['b', 'C', 'a', 'C', 'b']],
    'B': [['A', 'C'], ['b', 'S'], ['a', 'A', 'a']],
    'C': [['ε'], ['A', 'B']],
    'E': [['B', 'A']]
}
start_symbol = 'S'
```

Output:
```
CNF Productions:
X1 → b
X2 → a
X3 → X1A
X4 → X1X2
X5 → X4C
X6 → X1C
X7 → X6X2
X8 → X1C
X9 → X8X2
X10 → X9C
X11 → X1X2
X12 → X2A
S → X3C | X1A | X5X1 | X7X1 | X10X1 | X11X1 | a | X2S | X1S | X12X2 | AC
X13 → X1X2
X14 → X13C
X15 → X1C
X16 → X15X2
X17 → X1C
X18 → X17X2
X19 → X18C
X20 → X1X2
A → X14X1 | X16X1 | X19X1 | X20X1 | a | X2S
C → AB
X21 → X2A
X22 → X1X2
X23 → X22C
X24 → X1C
X25 → X24X2
X26 → X1C
X27 → X26X2
X28 → X27C
X29 → X1X2
B → X1S | X21X2 | AC | X23X1 | X25X1 | X28X1 | X29X1 | a | X2S
```

In conclusion, the implementation of the context-free grammar transformer effectively normalizes any given CFG into Chomsky Normal Form (CNF) through a series of well-structured and modular methods. It systematically eliminates ε-productions, unit productions, inaccessible symbols, and non-productive symbols, ensuring the grammar is simplified without altering the language it generates. The final transformation enforces CNF constraints by replacing terminals in long rules and decomposing multi-symbol productions into binary form using newly introduced variables.

## References
Cojuhari Irina, Duca Ludmila, Fiodorov Ion, (2022) *Formal Languages and Finite Automata Guide for practical lessons*

Wikipedia *Chomsky normal form*