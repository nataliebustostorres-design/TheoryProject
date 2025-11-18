#!/usr/bin/env python3

from automaton import AutomatonManager

def test_nfa_to_dfa_conversion():
    """Test NFA to DFA conversion"""
    print("Testing NFA to DFA conversion...")
    
    manager = AutomatonManager()
    
    # Create a simple NFA
    nfa = manager.nfa
    nfa.add_state('q0')
    nfa.add_state('q1')
    nfa.add_symbol('a')
    nfa.add_symbol('b')
    nfa.start = 'q0'
    nfa.finals.add('q1')
    nfa.add_transition('q0', 'a', 'q1')
    nfa.add_transition('q0', 'a', 'q0')
    nfa.add_transition('q0', 'b', 'q0')
    nfa.add_transition('q1', 'a', 'q1')
    nfa.add_transition('q1', 'b', 'q0')
    
    print("Original NFA:")
    print(nfa.formal_definition())
    print("\nNFA Transition Table:")
    header, rows = nfa.transition_table()
    print(f"{header[0]:>5}", end="")
    for h in header[1:]:
        print(f"{h:>8}", end="")
    print()
    for row in rows:
        print(f"{row[0]:>5}", end="")
        for cell in row[1:]:
            print(f"{cell:>8}", end="")
        print()
    
    # Convert to DFA
    success, message = manager.convert_to_dfa()
    if success:
        print(f"\n{message}")
        print("\nResulting DFA:")
        print(manager.dfa.formal_definition())
        print("\nDFA Transition Table:")
        header, rows = manager.dfa.transition_table()
        print(f"{header[0]:>5}", end="")
        for h in header[1:]:
            print(f"{h:>8}", end="")
        print()
        for row in rows:
            print(f"{row[0]:>5}", end="")
            for cell in row[1:]:
                print(f"{cell:>8}", end="")
            print()
        
        print("\nState Mapping:")
        for dfa_state, nfa_subset in manager.state_map.items():
            if isinstance(nfa_subset, frozenset):
                nfa_list = sorted(list(nfa_subset))
            else:
                nfa_list = [nfa_subset] if nfa_subset else []
            print(f"{dfa_state} = {{{', '.join(nfa_list)}}}")
    else:
        print(f"Conversion failed: {message}")

def test_epsilon_support():
    print("\n\nTesting epsilon support...")
    
    manager = AutomatonManager()
    nfa = manager.nfa
    
    # Add epsilon symbol
    nfa.add_symbol('ε')
    nfa.add_symbol('a')
    nfa.add_state('q0')
    nfa.add_state('q1')
    nfa.start = 'q0'
    nfa.finals.add('q1')
    nfa.add_transition('q0', 'ε', 'q1')
    nfa.add_transition('q0', 'a', 'q1')
    
    print("NFA with epsilon:")
    print(nfa.formal_definition())
    print(f"Has epsilon: {nfa.has_epsilon()}")

def test_load_sample():
    print("\n\nTesting load sample...")
    
    manager = AutomatonManager()
    manager.load_sample_data()
    
    print("Sample NFA loaded:")
    print(manager.nfa.formal_definition())

if __name__ == "__main__":
    test_nfa_to_dfa_conversion()
    test_epsilon_support()
    test_load_sample()
    print("\n\nAll tests completed!")