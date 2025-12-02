import base64
import io
import json
import os

import eel

from automaton import AutomatonManager

try:
    import graphviz
    HAS_GRAPHVIZ = True
except Exception:
    HAS_GRAPHVIZ = False


manager = AutomatonManager()


def _automaton_to_graph_png(automaton):
    """Render automaton to PNG bytes using graphviz (if available)."""
    if not HAS_GRAPHVIZ:
        return None

    g = graphviz.Digraph('Automaton', format='png')
    g.attr(rankdir='LR')

    for s in automaton.states:
        if s in automaton.finals:
            g.node(s, shape='doublecircle')
        else:
            g.node(s)

    if automaton.start:
        g.node('__start__', shape='point')
        g.edge('__start__', automaton.start)

    for s in automaton.states:
        # transitions can be set/list (NFA) or single value (DFA)
        trans = getattr(automaton, 'transitions', {})
        if s in trans:
            for sym, dests in trans[s].items():
                if isinstance(dests, (set, frozenset, list)):
                    for d in dests:
                        g.edge(s, d, label=sym)
                else:
                    if dests is not None:
                        g.edge(s, dests, label=sym)

    try:
        png = g.pipe(format='png')
        return png
    except Exception:
        return None


eel.init('web')


@eel.expose
def get_definition():
    return manager.get_current_automaton().formal_definition()


@eel.expose
def get_transition_table():
    header, rows = manager.get_current_automaton().transition_table()
    return {'header': header, 'rows': rows}


@eel.expose
def get_serialized():
    # Return the automaton as a serializable dict
    automaton = manager.get_current_automaton()
    return automaton.save_to_dict()


@eel.expose
def add_state(name):
    try:
        manager.get_current_automaton().add_state(name)
        return True, 'State added'
    except Exception as e:
        return False, str(e)


@eel.expose
def delete_state(name):
    try:
        manager.get_current_automaton().delete_state(name)
        return True, 'State deleted'
    except Exception as e:
        return False, str(e)


@eel.expose
def add_symbol(sym):
    try:
        manager.get_current_automaton().add_symbol(sym)
        return True, 'Symbol added'
    except Exception as e:
        return False, str(e)


@eel.expose
def delete_symbol(sym):
    try:
        manager.get_current_automaton().delete_symbol(sym)
        return True, 'Symbol deleted'
    except Exception as e:
        return False, str(e)


@eel.expose
def add_transition(src, sym, tgt):
    try:
        manager.get_current_automaton().add_transition(src, sym, tgt)
        return True, 'Transition added'
    except Exception as e:
        return False, str(e)


@eel.expose
def delete_transition(src, sym, tgt):
    try:
        manager.get_current_automaton().delete_transition(src, sym, tgt)
        return True, 'Transition deleted'
    except Exception as e:
        return False, str(e)


@eel.expose
def set_start(name):
    try:
        manager.get_current_automaton().start = name
        return True, 'Start set'
    except Exception as e:
        return False, str(e)


@eel.expose
def toggle_final(name):
    try:
        cur = manager.get_current_automaton()
        if name in cur.finals:
            cur.finals.discard(name)
        else:
            cur.finals.add(name)
        return True, 'Toggled final'
    except Exception as e:
        return False, str(e)


@eel.expose
def load_sample():
    try:
        manager.load_sample_data()
        return True, 'Sample loaded'
    except Exception as e:
        return False, str(e)


@eel.expose
def reset_automaton():
    try:
        manager.reset_automaton()
        return True, 'Reset'
    except Exception as e:
        return False, str(e)


@eel.expose
def convert_nfa_to_dfa():
    success, message = manager.convert_to_dfa()
    return success, message


@eel.expose
def set_mode(mode: str):
    try:
        manager.set_mode(mode.upper())
        return True, f"Mode set to {mode.upper()}"
    except Exception as e:
        return False, str(e)


@eel.expose
def is_dfa_available():
    try:
        return bool(manager.dfa.states)
    except Exception:
        return False


@eel.expose
def get_mode():
    try:
        return manager.mode
    except Exception:
        return 'NFA'


@eel.expose
def simulate_current(input_str):
    return manager.simulate_current(input_str)


@eel.expose
def simulate_dfa(input_str):
    return manager.simulate_dfa(input_str)


@eel.expose
def render_png_base64():
    automaton = manager.get_current_automaton()
    png = _automaton_to_graph_png(automaton)
    if png is None:
        return None
    return base64.b64encode(png).decode('ascii')


@eel.expose
def render_png_base64_for(mode: str = None):
    """Render PNG for a specific automaton mode.

    mode: None or 'current' -> current automaton (manager.mode)
          'NFA' -> render manager.nfa
          'DFA' -> render manager.dfa
    Returns base64 PNG or None
    """
    if mode is None or mode.lower() == 'current':
        automaton = manager.get_current_automaton()
    else:
        m = mode.upper()
        if m == 'NFA':
            automaton = manager.nfa
        elif m == 'DFA':
            automaton = manager.dfa
        else:
            automaton = manager.get_current_automaton()

    png = _automaton_to_graph_png(automaton)
    if png is None:
        return None
    return base64.b64encode(png).decode('ascii')


if __name__ == '__main__':
    # Start the Eel web UI. Developer can run `python3 -m pip install -r requirements.txt` first.
    port = int(os.environ.get('PORT', 0)) or 0
    # Use block=False to avoid blocking from some environments; let Eel choose a free port if 0.
    eel.start('index.html', size=(1200, 800))


