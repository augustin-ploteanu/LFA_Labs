from typing import List, Dict, Set, Tuple

class CFG:
    def __init__(self, variables: Set[str], terminals: Set[str], productions: Dict[str, List[List[str]]], start_symbol: str):
        self.variables = variables
        self.terminals = terminals
        self.productions = productions
        self.start_symbol = start_symbol
        self.new_var_counter = 1

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

    def display(self):
        for var in self.productions:
            rule_strs = [''.join(rule) for rule in self.productions[var]]
            print(f"{var} → {' | '.join(rule_strs)}")

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

'''
variables = {'S', 'A', 'B', 'C', 'D', 'E'}
terminals = {'a', 'b'}
productions = {
    'S': [['a', 'B'], ['A', 'C']],
    'A': [['a'], ['A', 'S', 'C'], ['B', 'C'], ['a', 'D']],
    'B': [['b'], ['b', 'S']],
    'C': [['ε'], ['B', 'A']],
    'D': [['a', 'b', 'C']],
    'E': [['a', 'B']]
}
start_symbol = 'S'
'''

cfg = CFG(variables, terminals, productions, start_symbol)

print("Initial Grammar Productions:")
cfg.display()
cfg.eliminate_epsilon_productions()
cfg.eliminate_unit_productions()
cfg.eliminate_inaccessible_symbols()
cfg.eliminate_nonproductive_symbols()
cfg.to_cnf()
print("\nCNF Productions:")
cfg.display()