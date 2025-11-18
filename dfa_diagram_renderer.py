import math

try:
    import graphviz
    HAS_GRAPHVIZ = True
except Exception:
    HAS_GRAPHVIZ = False


class DFADiagramRenderer:
    def __init__(self, canvas):
        self.canvas = canvas
        self.diagram_img = None

    def render_dfa_diagram(self, automaton):
        if HAS_GRAPHVIZ:
            try:
                self._render_with_graphviz(automaton)
                return
            except Exception as e:
                print('Graphviz render failed:', e)
        self._render_canvas_diagram(automaton)

    def _render_with_graphviz(self, automaton):
        g = graphviz.Digraph('DFA', format='png')
        g.attr(rankdir='LR', size='12,8', dpi='100')
        g.attr('node', fontsize='12', width='0.8', height='0.8')
        g.attr('edge', fontsize='10')
        
        # Add states
        for s in automaton.states:
            if s in automaton.finals:
                g.node(s, shape='doublecircle')
            else:
                g.node(s, shape='circle')
        
        # Add start arrow
        if automaton.start:
            g.node('__start__', shape='point', width='0')
            g.edge('__start__', automaton.start, color='green', penwidth='2')
        
        # Add transitions (DFA has single destinations)
        for s in automaton.states:
            if s in automaton.transitions:
                for sym, dest in automaton.transitions[s].items():
                    if dest is not None:
                        g.edge(s, dest, label=sym, color='blue')
        
        # Render to PNG and display
        png = g.pipe(format='png')
        try:
            from PIL import Image, ImageTk
            import io
            img = Image.open(io.BytesIO(png))
            canvas_width = self.canvas.winfo_width() or 900
            canvas_height = self.canvas.winfo_height() or 600
            
            # Scale image to fit canvas with padding
            img_ratio = img.width / img.height
            canvas_ratio = canvas_width / canvas_height
            
            if img_ratio > canvas_ratio:
                # Image is wider, fit to width
                new_width = canvas_width - 40
                new_height = int(new_width / img_ratio)
            else:
                # Image is taller, fit to height
                new_height = canvas_height - 40
                new_width = int(new_height * img_ratio)
            
            img = img.resize((new_width, new_height), Image.LANCZOS)
            self.diagram_img = ImageTk.PhotoImage(img)
            self.canvas.delete('all')
            
            # Center the image
            x_offset = (canvas_width - new_width) // 2
            y_offset = (canvas_height - new_height) // 2
            self.canvas.create_image(x_offset, y_offset, anchor='nw', image=self.diagram_img)
            
        except Exception as e:
            print(f"PIL rendering failed: {e}")
            self._render_canvas_diagram(automaton)

    def _render_canvas_diagram(self, automaton):
        self.canvas.delete('all')
        n = len(automaton.states)
        
        if n == 0:
            canvas_width = self.canvas.winfo_width() or 900
            canvas_height = self.canvas.winfo_height() or 600
            self.canvas.create_text(canvas_width//2, canvas_height//2, 
                                  text='No states to display', font=('Arial', 16, 'bold'))
            return
        
        # Use larger virtual canvas dimensions for better spacing
        canvas_width = 1200
        canvas_height = 800
        
        # Calculate layout parameters for larger canvas
        margin = 120
        cx, cy = canvas_width // 2, canvas_height // 2
        
        # Much larger radius for better spacing
        if n <= 3:
            r = 180
        elif n <= 6:
            r = 250
        else:
            r = 320
        
        # Ensure minimum radius
        r = max(r, 120)
        
        coords = {}
        
        # Position states in a circle
        if n == 1:
            coords[automaton.states[0]] = (cx, cy)
        else:
            angle_step = 2 * math.pi / n
            for i, state in enumerate(automaton.states):
                angle = i * angle_step - math.pi/2  # Start from top
                x = cx + r * math.cos(angle)
                y = cy + r * math.sin(angle)
                coords[state] = (x, y)
        
        # Draw states with larger, more visible elements
        state_radius = 35  # Increased from 25
        for state in automaton.states:
            x, y = coords[state]
            
            # Draw main circle with better colors
            self.canvas.create_oval(x-state_radius, y-state_radius, 
                                  x+state_radius, y+state_radius, 
                                  fill='#87CEEB', outline='#000080', width=3)
            
            # Draw final state indicator with better visibility
            if state in automaton.finals:
                self.canvas.create_oval(x-state_radius-8, y-state_radius-8, 
                                      x+state_radius+8, y+state_radius+8, 
                                      outline='#DC143C', width=4, fill='')
            
            # State label with larger font
            self.canvas.create_text(x, y, text=state, font=('Arial', 14, 'bold'), fill='black')
        
        # Draw start arrow with better visibility
        if automaton.start and automaton.start in coords:
            x, y = coords[automaton.start]
            start_x = max(margin, x - 100)
            self.canvas.create_line(start_x, y, x-state_radius-8, y, 
                                  arrow='last', fill='#228B22', width=4, 
                                  arrowshape=(16, 20, 6))
            self.canvas.create_text(start_x - 30, y, text='START', 
                                  font=('Arial', 12, 'bold'), fill='#228B22')
        
        # Group transitions by state pairs to handle multiple symbols
        transition_groups = {}
        for src in automaton.states:
            if src in automaton.transitions:
                for sym, dest in automaton.transitions[src].items():
                    if dest is not None and dest in coords:
                        key = (src, dest)
                        if key not in transition_groups:
                            transition_groups[key] = []
                        transition_groups[key].append(sym)
        
        # Draw transitions with better visibility
        for (src, dest), symbols in transition_groups.items():
            x1, y1 = coords[src]
            x2, y2 = coords[dest]
            label = ', '.join(sorted(symbols))
            
            if src == dest:  # Self-loop
                self._draw_self_loop(x1, y1, label, state_radius)
            else:
                self._draw_transition_arrow(x1, y1, x2, y2, label, state_radius)
    
    def _draw_self_loop(self, x, y, label, state_radius):
        loop_radius = 45  # Increased size
        # Position loop above the state
        loop_y = y - state_radius - loop_radius
        
        # Draw arc with better visibility
        self.canvas.create_arc(x-loop_radius, loop_y-loop_radius, 
                             x+loop_radius, loop_y+loop_radius,
                             start=30, extent=300, style='arc', 
                             outline='#0000CD', width=3)
        
        # Add larger arrowhead
        arrow_x = x + loop_radius * 0.7
        arrow_y = loop_y + loop_radius * 0.3
        self.canvas.create_polygon(arrow_x, arrow_y, 
                                 arrow_x-12, arrow_y-6, 
                                 arrow_x-12, arrow_y+6,
                                 fill='#0000CD', outline='#0000CD')
        
        # Label with background and larger font
        label_y = loop_y - loop_radius - 20
        text_width = len(label) * 8
        self.canvas.create_rectangle(x - text_width//2 - 5, label_y - 12,
                                   x + text_width//2 + 5, label_y + 12,
                                   fill='white', outline='gray', width=1)
        self.canvas.create_text(x, label_y, text=label, 
                              font=('Arial', 13, 'bold'), fill='#0000CD')
    
    def _draw_transition_arrow(self, x1, y1, x2, y2, label, state_radius):
        # Calculate direction vector
        dx, dy = x2 - x1, y2 - y1
        length = math.sqrt(dx*dx + dy*dy)
        
        if length == 0:
            return
        
        # Normalize direction
        dx, dy = dx/length, dy/length
        
        # Calculate start and end points (adjusted for larger state circles)
        start_x = x1 + dx * (state_radius + 8)
        start_y = y1 + dy * (state_radius + 8)
        end_x = x2 - dx * (state_radius + 8)
        end_y = y2 - dy * (state_radius + 8)
        
        # Draw arrow with better visibility
        self.canvas.create_line(start_x, start_y, end_x, end_y,
                              arrow='last', fill='#0000CD', width=3,
                              arrowshape=(16, 20, 6))
        
        # Calculate label position (offset from midpoint)
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2
        
        # Offset label perpendicular to the line
        perp_x = -dy * 25
        perp_y = dx * 25
        label_x = mid_x + perp_x
        label_y = mid_y + perp_y
        
        # Draw label background with border
        text_width = len(label) * 8
        self.canvas.create_rectangle(label_x - text_width//2 - 5, label_y - 12,
                                   label_x + text_width//2 + 5, label_y + 12,
                                   fill='white', outline='gray', width=1)
        
        # Draw label with larger font
        self.canvas.create_text(label_x, label_y, text=label,
                              font=('Arial', 13, 'bold'), fill='#0000CD')