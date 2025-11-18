
import math


try:
    import graphviz
    HAS_GRAPHVIZ = True
except Exception:
    HAS_GRAPHVIZ = False


class DiagramRenderer:
    
    def __init__(self, canvas):
        self.canvas = canvas
        self.diagram_img = None

    def render_nfa_diagram(self, automaton):

        if HAS_GRAPHVIZ:
            try:
                self._render_with_graphviz(automaton)
                return
            except Exception as e:
                print('Graphviz render failed:', e)
        self._render_simple_canvas(automaton)

    def _render_with_graphviz(self, automaton):
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
        
        # Handle both NFA and DFA transitions
        for s in automaton.states:
            if hasattr(automaton.transitions[s], 'items'):
                for sym, dests in automaton.transitions[s].items():
                    # Handle NFA (set of destinations) vs DFA (single destination)
                    if isinstance(dests, (set, frozenset, list)):
                        for d in dests:
                            g.edge(s, d, label=sym)
                    else:
                        if dests is not None:
                            g.edge(s, dests, label=sym)
        
        # Render to PNG and display
        png = g.pipe(format='png')
        try:
            from PIL import Image, ImageTk
            import io
            img = Image.open(io.BytesIO(png))
            canvas_width = self.canvas.winfo_width() or 900
            canvas_height = self.canvas.winfo_height() or 600
            img = img.resize((canvas_width-20, canvas_height-20), Image.LANCZOS)
            self.diagram_img = ImageTk.PhotoImage(img)
            self.canvas.delete('all')
            self.canvas.create_image(10, 10, anchor='nw', image=self.diagram_img)
        except Exception:
            self._render_simple_canvas(automaton)

    def _render_simple_canvas(self, automaton):

        self.canvas.delete('all')
        n = len(automaton.states)
        if n == 0:
            canvas_width = self.canvas.winfo_width() or 350
            canvas_height = self.canvas.winfo_height() or 250
            self.canvas.create_text(canvas_width//2, canvas_height//2, text='No states to display', font=('Arial', 12))
            return
        
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width() or 900
        canvas_height = self.canvas.winfo_height() or 600
        
        cx, cy = canvas_width // 2, canvas_height // 2
        r = min(canvas_width // 3, canvas_height // 3, 150)
        
        # Better layout for small number of states
        if n <= 3:
            r = min(r, 80)
        
        angle_step = 2 * math.pi / max(1, n)
        coords = {}
        
        # Draw states
        for i, s in enumerate(automaton.states):
            if n == 1:
                x, y = cx, cy
            else:
                a = i * angle_step - math.pi/2  # Start from top
                x = cx + r * math.cos(a)
                y = cy + r * math.sin(a)
            coords[s] = (x, y)
            
            # Draw circle
            self.canvas.create_oval(x-20, y-20, x+20, y+20, fill='lightblue', outline='black', width=2)
            # Label
            self.canvas.create_text(x, y, text=s, font=('Arial', 11, 'bold'))
            # Final state double circle
            if s in automaton.finals:
                self.canvas.create_oval(x-25, y-25, x+25, y+25, outline='red', width=2)
        
        # Start arrow
        if automaton.start and automaton.start in coords:
            x, y = coords[automaton.start]
            start_x = max(50, x - 60)
            self.canvas.create_line(start_x, y, x-25, y, arrow='last', fill='green', width=3)
            self.canvas.create_text(start_x - 20, y, text='start', font=('Arial', 9), fill='green')
        
        # Transitions - handle both NFA and DFA
        transition_labels = {}  # To group multiple transitions between same states
        
        for s in automaton.states:
            x1, y1 = coords[s]
            
            # Check if this is NFA or DFA based on transition structure
            is_nfa = hasattr(automaton.transitions[s], 'items') and any(
                isinstance(dest, (set, frozenset, list)) and len(dest) > 1 
                for sym_dict in automaton.transitions[s].values() 
                for dest in [sym_dict] if isinstance(sym_dict, (set, frozenset, list))
            )
            
            if hasattr(automaton.transitions[s], 'items'):
                for sym, dests in automaton.transitions[s].items():
                    # Handle NFA (set of destinations) vs DFA (single destination)
                    if isinstance(dests, (set, frozenset, list)):
                        dest_list = list(dests)
                    else:
                        dest_list = [dests] if dests is not None else []
                    
                    for d in dest_list:
                        if d in coords:
                            x2, y2 = coords[d]
                            
                            # Create transition key for grouping
                            trans_key = (s, d)
                            if trans_key not in transition_labels:
                                transition_labels[trans_key] = []
                            transition_labels[trans_key].append(sym)
        
        # Draw transitions with grouped labels
        for (src, dest), symbols in transition_labels.items():
            x1, y1 = coords[src]
            x2, y2 = coords[dest]
            label = ', '.join(sorted(symbols))
            
            if src == dest:  # Self-loop
                loop_offset = 35
                self.canvas.create_arc(x1-loop_offset, y1-loop_offset, x1+loop_offset, y1+loop_offset, 
                                     start=45, extent=270, style='arc', outline='blue', width=2)
                self.canvas.create_text(x1, y1-loop_offset-15, text=label, font=('Arial', 10, 'bold'), 
                                      fill='blue')
            else:
                # Calculate arrow position to not overlap with circles
                dx, dy = x2 - x1, y2 - y1
                length = math.sqrt(dx*dx + dy*dy)
                if length > 0:
                    # Normalize and adjust for circle radius
                    dx, dy = dx/length, dy/length
                    start_x, start_y = x1 + dx*25, y1 + dy*25
                    end_x, end_y = x2 - dx*25, y2 - dy*25
                    
                    self.canvas.create_line(start_x, start_y, end_x, end_y, 
                                          arrow='last', fill='blue', width=2, arrowshape=(10,12,5))
                    
                    # Label position (slightly offset from midpoint)
                    mx, my = (start_x + end_x) / 2, (start_y + end_y) / 2
                    # Offset label perpendicular to line
                    perp_x, perp_y = -dy * 15, dx * 15
                    label_x, label_y = mx + perp_x, my + perp_y
                    
                    # Background for label
                    self.canvas.create_rectangle(label_x-len(label)*4, label_y-8, 
                                               label_x+len(label)*4, label_y+8, 
                                               fill='white', outline='white')
                    self.canvas.create_text(label_x, label_y, text=label, 
                                          font=('Arial', 10, 'bold'), fill='blue')