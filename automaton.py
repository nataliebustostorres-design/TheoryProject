"""
Automaton data structures and logic - separated from GUI
"""
import json
from collections import defaultdict, deque


class NFA:
    def __init__(self):
        self.states = []
        self.symbols = []
        self.start = None
        self.finals = set()
        self.transitions = defaultdict(lambda: defaultdict(set))
    
    def has_epsilon(self):
        """Check if NFA has epsilon transitions"""
        return 'ε' in self.symbols

    def epsilon_closure(self, states):
        """Compute epsilon closure of a set of states"""
        closure = set(states)
        stack = list(states)
        
        while stack:
            state = stack.pop()
            if state in self.transitions and 'ε' in self.transitions[state]:
                for next_state in self.transitions[state]['ε']:
                    if next_state not in closure:
                        closure.add(next_state)
                        stack.append(next_state)
        
        return closure

    def add_state(self, name):
        if name in self.states:
            raise ValueError('State already exists')
        self.states.append(name)

    def delete_state(self, name):
        if name not in self.states:
            raise ValueError('No such state')
        self.states.remove(name)
        if self.start == name:
            self.start = None
        self.finals.discard(name)
        if name in self.transitions:
            del self.transitions[name]
        for s in list(self.transitions.keys()):
            for sym in list(self.transitions[s].keys()):
                if name in self.transitions[s][sym]:
                    self.transitions[s][sym].discard(name)

    def add_symbol(self, sym):
        if sym in self.symbols:
            raise ValueError('Symbol exists')
        self.symbols.append(sym)

    def delete_symbol(self, sym):
        if sym not in self.symbols:
            raise ValueError('No such symbol')
        self.symbols.remove(sym)
        for s in self.transitions:
            if sym in self.transitions[s]:
                del self.transitions[s][sym]

    def add_transition(self, src, sym, tgt):
        if src not in self.states or tgt not in self.states:
            raise ValueError('Source/Target state not found')
        if sym not in self.symbols:
            raise ValueError('Symbol not in alphabet')
        self.transitions[src][sym].add(tgt)

    def delete_transition(self, src, sym, tgt):
        if src in self.transitions and sym in self.transitions[src] and tgt in self.transitions[src][sym]:
            self.transitions[src][sym].discard(tgt)

    def formal_definition(self):
        Q = '{' + ', '.join(self.states) + '}'
        Sigma = '{' + ', '.join(self.symbols) + '}'
        q0 = self.start or 'None'
        F = '{' + ', '.join(sorted(self.finals)) + '}'
        lines = [f'Q = {Q}', f'Σ = {Sigma}', f'q0 = {q0}', f'F = {F}', 'δ : Q × Σ → P(Q)', '']
        
        # Show transitions in a more organized way
        for s in self.states:
            for sym in self.symbols:
                dest = sorted(self.transitions[s].get(sym, []))
                if dest:
                    # Use format to safely include literal braces around the joined destinations
                    lines.append("    δ({}, {}) = {{{}}}".format(s, sym, ', '.join(dest)))
        return '\n'.join(lines)

    def transition_table(self):
        header = ['δ'] + self.symbols
        rows = []
        for s in self.states:
            row = [s]
            for sym in self.symbols:
                dest = sorted(self.transitions[s].get(sym, []))
                row.append('{' + ', '.join(dest) + '}' if dest else '{}')
            rows.append(row)
        return header, rows

    def accepts(self, input_str):
        if self.start is None:
            return False
        current = self.epsilon_closure(set([self.start]))
        for ch in input_str:
            if ch not in self.symbols:
                return False
            next_set = set()
            for s in current:
                dests = self.transitions[s].get(ch, [])
                next_set.update(dests)
            current = self.epsilon_closure(next_set)
            if not current:
                return False
        return any(s in self.finals for s in current)

    def to_dfa(self):
        if self.start is None:
            return DFA(), {}
        
        # Initialize with start state
        start_set = frozenset([self.start])
        queue = deque([start_set])
        seen = {start_set: 'q0'}
        dfa = DFA()
        dfa.add_state('q0')
        dfa.start = 'q0'
        
        # Check if start state is final
        if any(s in self.finals for s in start_set):
            dfa.finals.add('q0')
        
        # Add symbols to DFA (excluding epsilon if present)
        dfa_symbols = [sym for sym in self.symbols if sym != 'ε']
        for sym in dfa_symbols:
            dfa.add_symbol(sym)

        state_id = 1
        while queue:
            sset = queue.popleft()
            src_name = seen[sset]
            
            for sym in dfa_symbols:
                dest = set()
                for s in sset:
                    if s in self.transitions and sym in self.transitions[s]:
                        dest.update(self.transitions[s][sym])
                
                dest_frozen = frozenset(dest)
                
                # Handle empty destination (dead state)
                if not dest_frozen:
                    # Create dead state if not exists
                    if frozenset() not in seen:
                        dead_name = f'q{state_id}'
                        state_id += 1
                        seen[frozenset()] = dead_name
                        dfa.add_state(dead_name)
                        # Dead state transitions to itself for all symbols
                        for dead_sym in dfa_symbols:
                            dfa.add_transition(dead_name, dead_sym, dead_name)
                    dfa.add_transition(src_name, sym, seen[frozenset()])
                else:
                    # Handle non-empty destination
                    if dest_frozen not in seen:
                        name = f'q{state_id}'
                        state_id += 1
                        seen[dest_frozen] = name
                        dfa.add_state(name)
                        if any(x in self.finals for x in dest_frozen):
                            dfa.finals.add(name)
                        queue.append(dest_frozen)
                    
                    dfa.add_transition(src_name, sym, seen[dest_frozen])
        
        return dfa, seen

    def save_to_dict(self):
        return {
            'states': self.states,
            'symbols': self.symbols,
            'start': self.start,
            'finals': list(self.finals),
            'transitions': {s: {sym: list(dests) for sym, dests in self.transitions[s].items()} for s in self.transitions}
        }

    def load_from_dict(self, data):
        self.__init__()
        for s in data.get('states', []):
            self.add_state(s)
        for sym in data.get('symbols', []):
            self.add_symbol(sym)
        self.start = data.get('start')
        for fstate in data.get('finals', []):
            self.finals.add(fstate)
        for s, syms in data.get('transitions', {}).items():
            for sym, dests in syms.items():
                for d in dests:
                    self.add_transition(s, sym, d)


class DFA:
    def __init__(self):
        self.states = []
        self.symbols = []
        self.start = None
        self.finals = set()
        self.transitions = defaultdict(dict)

    def add_state(self, name):
        if name in self.states:
            raise ValueError('State already exists')
        self.states.append(name)

    def delete_state(self, name):
        if name not in self.states:
            raise ValueError('No such state')
        self.states.remove(name)
        if self.start == name:
            self.start = None
        self.finals.discard(name)
        if name in self.transitions:
            del self.transitions[name]
        for s in list(self.transitions.keys()):
            for sym in list(self.transitions[s].keys()):
                if self.transitions[s][sym] == name:
                    del self.transitions[s][sym]

    def add_symbol(self, sym):
        if sym in self.symbols:
            raise ValueError('Symbol exists')
        self.symbols.append(sym)

    def delete_symbol(self, sym):
        if sym not in self.symbols:
            raise ValueError('No such symbol')
        self.symbols.remove(sym)
        for s in self.transitions:
            if sym in self.transitions[s]:
                del self.transitions[s][sym]

    def add_transition(self, src, sym, tgt):
        if src not in self.states or tgt not in self.states:
            raise ValueError('Source/Target state not found')
        if sym not in self.symbols:
            raise ValueError('Symbol not in alphabet')
        self.transitions[src][sym] = tgt

    def delete_transition(self, src, sym, tgt):
        if src in self.transitions and sym in self.transitions[src] and self.transitions[src][sym] == tgt:
            del self.transitions[src][sym]

    def formal_definition(self):
        Q = '{' + ', '.join(self.states) + '}'
        Sigma = '{' + ', '.join(self.symbols) + '}'
        q0 = self.start or 'None'
        F = '{' + ', '.join(sorted(self.finals)) + '}'
        lines = [f'Q = {Q}', f'Σ = {Sigma}', f'q0 = {q0}', f'F = {F}', 'δ : Q × Σ → Q', '']
        
        # Show transitions in a more organized way
        for s in self.states:
            for sym in self.symbols:
                dest = self.transitions.get(s, {}).get(sym)
                if dest is not None:
                    lines.append(f'    δ({s}, {sym}) = {dest}')
        return '\n'.join(lines)

    def transition_table(self):
        header = ['δ'] + self.symbols
        rows = []
        for s in self.states:
            row = [s]
            for sym in self.symbols:
                dest = self.transitions.get(s, {}).get(sym, '')
                row.append(dest)
            rows.append(row)
        return header, rows

    def accepts(self, input_str):
        if self.start is None:
            return False
        cur = self.start
        for ch in input_str:
            if ch not in self.symbols:
                return False
            cur = self.transitions.get(cur, {}).get(ch)
            if cur is None:
                return False
        return cur in self.finals

    def save_to_dict(self):
        return {
            'states': self.states,
            'symbols': self.symbols,
            'start': self.start,
            'finals': list(self.finals),
            'transitions': dict(self.transitions)
        }

    def load_from_dict(self, data):
        self.__init__()
        for s in data.get('states', []):
            self.add_state(s)
        for sym in data.get('symbols', []):
            self.add_symbol(sym)
        self.start = data.get('start')
        for fstate in data.get('finals', []):
            self.finals.add(fstate)
        for s, syms in data.get('transitions', {}).items():
            for sym, dest in syms.items():
                self.transitions[s][sym] = dest


class AutomatonManager:
    """Manager class to handle automaton operations"""
    
    def __init__(self):
        self.nfa = NFA()
        self.dfa = DFA()
        self.state_map = {}
        self.mode = 'NFA'  # 'NFA' or 'DFA'
    
    def set_mode(self, mode):
        """Set working mode to NFA or DFA"""
        self.mode = mode
    
    def get_current_automaton(self):
        """Get the currently active automaton based on mode"""
        return self.nfa if self.mode == 'NFA' else self.dfa

    def reset_automaton(self):
        """Reset the current automaton based on mode"""
        if self.mode == 'NFA':
            self.nfa = NFA()
        else:
            self.dfa = DFA()
        self.state_map.clear()

    def convert_to_dfa(self):
        if not self.nfa.states:
            return False, "NFA is empty"
        try:
            result = self.nfa.to_dfa()
            if isinstance(result, tuple):
                dfa, mapping = result
                self.dfa = dfa
                inv = {}
                for k, v in mapping.items():
                    inv[v] = k
                self.state_map = inv
                return True, "NFA converted to DFA"
            else:
                self.dfa = result
                self.state_map = {}
                return True, "NFA converted to DFA"
        except Exception as e:
            return False, str(e)

    def load_sample_data(self):
        """Load sample NFA that accepts strings ending with 'a'"""
        self.nfa = NFA()
        self.nfa.add_state('q0')
        self.nfa.add_state('q1')
        self.nfa.add_symbol('a')
        self.nfa.add_symbol('b')
        self.nfa.start = 'q0'
        self.nfa.finals.add('q1')
        self.nfa.add_transition('q0', 'a', 'q1')
        self.nfa.add_transition('q0', 'a', 'q0')
        self.nfa.add_transition('q0', 'b', 'q0')
        self.nfa.add_transition('q1', 'a', 'q1')
        self.nfa.add_transition('q1', 'b', 'q0')

    def save_to_file(self, filepath):
        try:
            data = self.nfa.save_to_dict() if self.mode == 'NFA' else self.dfa.save_to_dict()
            data['mode'] = self.mode
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return True, f"Saved {self.mode} to {filepath}"
        except Exception as e:
            return False, str(e)

    def load_from_file(self, filepath):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            self.mode = data.get('mode', 'NFA')
            if self.mode == 'NFA':
                self.nfa.load_from_dict(data)
            else:
                self.dfa.load_from_dict(data)
            return True, f"Loaded {self.mode} from {filepath}"
        except Exception as e:
            return False, str(e)

    def simulate_current(self, input_str):
        """Simulate current automaton based on mode"""
        if self.mode == 'NFA':
            return self.simulate_nfa(input_str)
        else:
            return self.simulate_dfa(input_str)
    
    def simulate_nfa(self, input_str):
        """Simulate NFA and return result with trace"""
        if self.nfa.start is None:
            return {'accepted': False, 'message': 'No start state', 'steps': []}

        # Build human-friendly steps (no Python brackets)
        current = self.nfa.epsilon_closure({self.nfa.start})
        def fmt(states):
            if not states:
                return '∅'
            return ', '.join(sorted(states))

        steps = []
        steps.append(f"Starting at: {fmt(current)}")

        step_no = 1
        for ch in input_str:
            if ch not in self.nfa.symbols:
                return {'accepted': False, 'message': f'Invalid symbol "{ch}"', 'steps': steps}
            next_set = set()
            for state in current:
                next_set.update(self.nfa.transitions[state].get(ch, []))
            current = self.nfa.epsilon_closure(next_set)
            steps.append(f"{step_no}) After input '{ch}' -> {fmt(current)}")
            step_no += 1
            if not current:
                return {'accepted': False, 'message': 'Dead end', 'steps': steps}

        accepted = any(s in self.nfa.finals for s in current)
        steps.append(f"Final states reached: {fmt(current)}")
        return {'accepted': accepted, 'message': 'ACCEPT' if accepted else 'REJECT', 'steps': steps}

    def simulate_dfa(self, input_str):
        """Simulate DFA and return result with trace"""
        if self.dfa.start is None:
            return {'accepted': False, 'message': 'No start state', 'steps': []}

        def fmt_state(s):
            return s if s is not None else '∅'

        cur = self.dfa.start
        steps = [f"Starting at: {fmt_state(cur)}"]
        step_no = 1

        for ch in input_str:
            if ch not in self.dfa.symbols:
                return {'accepted': False, 'message': f'Invalid symbol "{ch}"', 'steps': steps}
            next_state = self.dfa.transitions.get(cur, {}).get(ch)
            steps.append(f"{step_no}) Input '{ch}' -> {fmt_state(next_state)}")
            step_no += 1
            if next_state is None:
                return {'accepted': False, 'message': 'Dead end', 'steps': steps}
            cur = next_state

        accepted = cur in self.dfa.finals
        steps.append(f"Final state reached: {fmt_state(cur)}")
        return {'accepted': accepted, 'message': 'ACCEPT' if accepted else 'REJECT', 'steps': steps}