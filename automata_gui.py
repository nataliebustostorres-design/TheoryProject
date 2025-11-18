import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from automaton import AutomatonManager
from diagram_renderer import DiagramRenderer


class AutomataGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Automata GUI - NFA & DFA')
        self.geometry('1200x800')
        self.minsize(1000, 600)
        
        # Use the separated logic
        self.manager = AutomatonManager()
        
        self._build_ui()
        self._bind_shortcuts()
        self.refresh_all()

    def _build_ui(self):
        """Build the improved UI layout"""
        # Create main paned window for better space management
        main_paned = ttk.PanedWindow(self, orient='horizontal')
        main_paned.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left panel - Controls (narrower)
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        # Right panel - Display and simulation
        right_paned = ttk.PanedWindow(main_paned, orient='vertical')
        main_paned.add(right_paned, weight=3)
        
        self._build_controls(left_frame)
        self._build_display_panels(right_paned)

    def _build_controls(self, parent):
        """Build the control panel"""
        # Scrollable frame for controls
        canvas = tk.Canvas(parent, width=280)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # States section
        self._build_states_section(scrollable_frame)
        
        # Symbols section
        self._build_symbols_section(scrollable_frame)
        
        # Start/Final states section
        self._build_start_final_section(scrollable_frame)
        
        # Transitions section
        self._build_transitions_section(scrollable_frame)
        
        # Utilities section
        self._build_utilities_section(scrollable_frame)

    def _build_states_section(self, parent):
        """Build states control section"""
        frame = ttk.LabelFrame(parent, text='States')
        frame.pack(fill='x', padx=5, pady=3)
        
        entry_frame = ttk.Frame(frame)
        entry_frame.pack(fill='x', padx=3, pady=3)
        
        self.state_entry = ttk.Entry(entry_frame)
        self.state_entry.pack(side='left', fill='x', expand=True, padx=(0,3))
        
        btn_frame = ttk.Frame(entry_frame)
        btn_frame.pack(side='right')
        
        ttk.Button(btn_frame, text='Add', command=self.add_state, width=6).pack(side='left', padx=1)
        ttk.Button(btn_frame, text='Del', command=self.delete_state, width=6).pack(side='left', padx=1)
        
        self.states_listbox = tk.Listbox(frame, height=4, exportselection=False)
        self.states_listbox.pack(fill='x', padx=3, pady=3)

    def _build_symbols_section(self, parent):
        """Build symbols control section"""
        frame = ttk.LabelFrame(parent, text='Alphabet')
        frame.pack(fill='x', padx=5, pady=3)
        
        entry_frame = ttk.Frame(frame)
        entry_frame.pack(fill='x', padx=3, pady=3)
        
        self.sym_entry = ttk.Entry(entry_frame)
        self.sym_entry.pack(side='left', fill='x', expand=True, padx=(0,3))
        
        btn_frame = ttk.Frame(entry_frame)
        btn_frame.pack(side='right')
        
        ttk.Button(btn_frame, text='Add', command=self.add_symbol, width=6).pack(side='left', padx=1)
        ttk.Button(btn_frame, text='Del', command=self.delete_symbol, width=6).pack(side='left', padx=1)
        
        self.symbols_listbox = tk.Listbox(frame, height=3, exportselection=False)
        self.symbols_listbox.pack(fill='x', padx=3, pady=3)
        
        # Epsilon button for NFA only
        self.epsilon_btn = ttk.Button(frame, text='Add ε (Epsilon)', command=self.add_epsilon)
        # Initially pack it since we start in NFA mode
        self.epsilon_btn.pack(fill='x', padx=3, pady=1)

    def _build_start_final_section(self, parent):
        """Build start/final states section"""
        frame = ttk.LabelFrame(parent, text='Start / Final')
        frame.pack(fill='x', padx=5, pady=3)
        
        ttk.Button(frame, text='Set Start', command=self.set_start_state).pack(fill='x', padx=3, pady=1)
        ttk.Button(frame, text='Toggle Final', command=self.toggle_final_state).pack(fill='x', padx=3, pady=1)
        
        self.start_label = ttk.Label(frame, text='Start: None', font=('Arial', 8))
        self.start_label.pack(padx=3, pady=1)
        
        self.final_label = ttk.Label(frame, text='Finals: {}', font=('Arial', 8))
        self.final_label.pack(padx=3, pady=1)

    def _build_transitions_section(self, parent):
        """Build transitions section"""
        frame = ttk.LabelFrame(parent, text='Transitions')
        frame.pack(fill='x', padx=5, pady=3)
        
        ttk.Label(frame, text='Symbol:', font=('Arial', 8)).pack(anchor='w', padx=3)
        self.trans_sym_combo = ttk.Combobox(frame, values=[], state='readonly', height=3)
        self.trans_sym_combo.pack(fill='x', padx=3, pady=1)
        
        ttk.Label(frame, text='Source:', font=('Arial', 8)).pack(anchor='w', padx=3)
        self.trans_src_combo = ttk.Combobox(frame, values=[], state='readonly', height=3)
        self.trans_src_combo.pack(fill='x', padx=3, pady=1)
        
        ttk.Label(frame, text='Target:', font=('Arial', 8)).pack(anchor='w', padx=3)
        self.trans_tgt_combo = ttk.Combobox(frame, values=[], state='readonly', height=3)
        self.trans_tgt_combo.pack(fill='x', padx=3, pady=1)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill='x', padx=3, pady=3)
        
        ttk.Button(btn_frame, text='Add', command=self.add_transition).pack(side='left', fill='x', expand=True, padx=(0,1))
        ttk.Button(btn_frame, text='Delete', command=self.delete_transition).pack(side='right', fill='x', expand=True, padx=(1,0))

    def _build_utilities_section(self, parent):
        """Build utilities section"""
        frame = ttk.LabelFrame(parent, text='Utilities')
        frame.pack(fill='x', padx=5, pady=3)
        
        # Mode selection
        mode_frame = ttk.LabelFrame(frame, text='Mode')
        mode_frame.pack(fill='x', padx=3, pady=3)
        
        self.mode_var = tk.StringVar(value='NFA')
        ttk.Radiobutton(mode_frame, text='NFA', variable=self.mode_var, value='NFA', command=self.on_mode_change).pack(side='left', padx=5)
        ttk.Radiobutton(mode_frame, text='DFA', variable=self.mode_var, value='DFA', command=self.on_mode_change).pack(side='left', padx=5)
        
        ttk.Button(frame, text='Convert NFA to DFA', command=self.convert_nfa_to_dfa).pack(fill='x', padx=3, pady=1)
        ttk.Button(frame, text='Load Sample', command=self.load_sample).pack(fill='x', padx=3, pady=1)
        ttk.Button(frame, text='Reset', command=self.reset_automaton).pack(fill='x', padx=3, pady=1)

    def _build_display_panels(self, parent):
        """Build display and simulation panels"""
        # Top panel - Formal definitions and tables
        top_frame = ttk.Frame(parent)
        parent.add(top_frame, weight=2)
        
        # Create notebook for NFA and DFA displays
        self.display_notebook = ttk.Notebook(top_frame)
        self.display_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Current automaton display
        self.display_frame = ttk.Frame(self.display_notebook)
        self.display_notebook.add(self.display_frame, text='Current Automaton (NFA)')
        self._build_automaton_display(self.display_frame)
        
        # DFA display (initially empty)
        self.dfa_display_frame = ttk.Frame(self.display_notebook)
        self.display_notebook.add(self.dfa_display_frame, text='Converted DFA')
        self._build_dfa_display(self.dfa_display_frame)
        
        # Bottom panel - Diagrams and simulation
        bottom_frame = ttk.Frame(parent)
        parent.add(bottom_frame, weight=1)
        
        # Split bottom into diagrams and simulation
        bottom_paned = ttk.PanedWindow(bottom_frame, orient='horizontal')
        bottom_paned.pack(fill='both', expand=True, padx=5, pady=5)
        
        self._build_diagrams_panel(bottom_paned)
        self._build_simulation_panel(bottom_paned)

    def _build_automaton_display(self, parent):
        """Build compact automaton display"""
        paned = ttk.PanedWindow(parent, orient='horizontal')
        paned.pack(fill='both', expand=True, padx=3, pady=3)
        
        # Formal definition (compact)
        def_frame = ttk.LabelFrame(paned, text='Definition')
        paned.add(def_frame, weight=1)
        
        self.automaton_text = tk.Text(def_frame, height=4, font=('Courier', 8))
        self.automaton_text.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Transition table (compact)
        table_frame = ttk.LabelFrame(paned, text='Transitions')
        paned.add(table_frame, weight=1)
        
        self.automaton_table = ttk.Treeview(table_frame, show='headings', height=4)
        self.automaton_table.pack(fill='both', expand=True, padx=2, pady=2)
    
    def _build_dfa_display(self, parent):
        """Build DFA display panel"""
        # Top section for definition and table
        top_paned = ttk.PanedWindow(parent, orient='horizontal')
        top_paned.pack(fill='both', expand=True, padx=3, pady=3)
        
        # Formal definition
        def_frame = ttk.LabelFrame(top_paned, text='DFA Definition')
        top_paned.add(def_frame, weight=1)
        
        self.dfa_text = tk.Text(def_frame, height=4, font=('Courier', 8))
        self.dfa_text.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Transition table
        table_frame = ttk.LabelFrame(top_paned, text='DFA Transitions')
        top_paned.add(table_frame, weight=1)
        
        self.dfa_table = ttk.Treeview(table_frame, show='headings', height=4)
        self.dfa_table.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Bottom section for DFA diagram
        diagram_frame = ttk.LabelFrame(parent, text='DFA Diagram')
        diagram_frame.pack(fill='both', expand=True, padx=3, pady=3)
        
        self.dfa_canvas = tk.Canvas(diagram_frame, width=400, height=250, bg='white')
        self.dfa_canvas.pack(fill='both', expand=True, padx=5, pady=5)
        
        btn_frame = ttk.Frame(diagram_frame)
        btn_frame.pack(pady=2)
        ttk.Button(btn_frame, text='Render DFA Diagram', command=self.render_dfa_diagram).pack()

    def _build_diagrams_panel(self, parent):
        """Build diagrams panel with tabs for NFA and DFA"""
        diag_frame = ttk.LabelFrame(parent, text='Diagrams')
        parent.add(diag_frame, weight=1)
        
        # Create notebook for NFA and DFA diagrams
        self.diagram_notebook = ttk.Notebook(diag_frame)
        self.diagram_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Current automaton diagram tab
        current_frame = ttk.Frame(self.diagram_notebook)
        self.diagram_notebook.add(current_frame, text='Current Automaton')
        
        self.canvas = tk.Canvas(current_frame, width=350, height=200, bg='white')
        self.canvas.pack(padx=5, pady=5)
        self.renderer = DiagramRenderer(self.canvas)
        ttk.Button(current_frame, text='Render Diagram', command=self.render_diagram).pack(pady=2)
        


    def _build_simulation_panel(self, parent):
        """Build simulation panel"""
        sim_frame = ttk.LabelFrame(parent, text='Simulation')
        parent.add(sim_frame, weight=1)
        
        ttk.Label(sim_frame, text='Input string:').pack(pady=3)
        self.input_entry = ttk.Entry(sim_frame, font=('Courier', 10))
        self.input_entry.pack(fill='x', padx=5, pady=3)
        
        btn_frame = ttk.Frame(sim_frame)
        btn_frame.pack(fill='x', padx=5, pady=3)
        
        ttk.Button(btn_frame, text='Test Current', command=self.test_current).pack(fill='x', padx=3, pady=1)
        ttk.Button(btn_frame, text='Test DFA', command=self.test_dfa).pack(fill='x', padx=3, pady=1)
        
        self.sim_result_label = ttk.Label(sim_frame, text='Result:', font=('Arial', 10, 'bold'))
        self.sim_result_label.pack(pady=3)
        
        ttk.Label(sim_frame, text='Trace:').pack(anchor='w', padx=5)
        
        trace_frame = ttk.Frame(sim_frame)
        trace_frame.pack(fill='both', expand=True, padx=5, pady=3)
        
        self.trace_text = tk.Text(trace_frame, height=8, font=('Courier', 8))
        trace_scroll = ttk.Scrollbar(trace_frame, orient='vertical', command=self.trace_text.yview)
        self.trace_text.configure(yscrollcommand=trace_scroll.set)
        
        self.trace_text.pack(side='left', fill='both', expand=True)
        trace_scroll.pack(side='right', fill='y')

    def _bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.bind('<F5>', lambda e: self.refresh_all())

    def on_mode_change(self):
        """Handle mode change between NFA and DFA"""
        mode = self.mode_var.get()
        self.manager.set_mode(mode)
        self.display_frame.config(text=f'Current Automaton ({mode})')
        
        # Show/hide epsilon button based on mode
        if mode == 'NFA':
            self.epsilon_btn.pack(fill='x', padx=3, pady=1)
        else:
            self.epsilon_btn.pack_forget()
        
        self.refresh_all()

    # Event handlers using the separated logic
    def add_state(self):
        name = self.state_entry.get().strip()
        if not name:
            messagebox.showwarning('Input', 'Enter a state name')
            return
        try:
            self.manager.get_current_automaton().add_state(name)
            self.state_entry.delete(0, 'end')
            self.refresh_all()
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def delete_state(self):
        sel = self.states_listbox.curselection()
        if not sel:
            messagebox.showwarning('Select', 'Select a state to delete')
            return
        name = self.states_listbox.get(sel[0])
        try:
            self.manager.get_current_automaton().delete_state(name)
            self.refresh_all()
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def add_symbol(self):
        sym = self.sym_entry.get().strip()
        if not sym:
            messagebox.showwarning('Input', 'Enter a symbol')
            return
        try:
            self.manager.get_current_automaton().add_symbol(sym)
            self.sym_entry.delete(0, 'end')
            self.refresh_all()
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def delete_symbol(self):
        sel = self.symbols_listbox.curselection()
        if not sel:
            messagebox.showwarning('Select', 'Select a symbol to delete')
            return
        name = self.symbols_listbox.get(sel[0])
        try:
            self.manager.get_current_automaton().delete_symbol(name)
            self.refresh_all()
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def set_start_state(self):
        sel = self.states_listbox.curselection()
        if not sel:
            messagebox.showwarning('Select', 'Select a state to set as start')
            return
        name = self.states_listbox.get(sel[0])
        self.manager.get_current_automaton().start = name
        self.refresh_all()

    def toggle_final_state(self):
        sel = self.states_listbox.curselection()
        if not sel:
            messagebox.showwarning('Select', 'Select a state to toggle final')
            return
        name = self.states_listbox.get(sel[0])
        current = self.manager.get_current_automaton()
        if name in current.finals:
            current.finals.discard(name)
        else:
            current.finals.add(name)
        self.refresh_all()

    def add_transition(self):
        sym = self.trans_sym_combo.get()
        src = self.trans_src_combo.get()
        tgt = self.trans_tgt_combo.get()
        if not sym or not src or not tgt:
            messagebox.showwarning('Select', 'Choose symbol, source, and target')
            return
        try:
            self.manager.get_current_automaton().add_transition(src, sym, tgt)
            self.refresh_all()
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def delete_transition(self):
        sym = self.trans_sym_combo.get()
        src = self.trans_src_combo.get()
        tgt = self.trans_tgt_combo.get()
        if not sym or not src or not tgt:
            messagebox.showwarning('Select', 'Choose symbol, source, and target')
            return
        self.manager.get_current_automaton().delete_transition(src, sym, tgt)
        self.refresh_all()

    def reset_automaton(self):
        mode = self.manager.mode
        if not messagebox.askyesno('Confirm', f'Reset the {mode} (clear everything)?'):
            return
        self.manager.reset_automaton()
        
        # Clear all diagrams
        self.canvas.delete('all')
        if hasattr(self, 'dfa_canvas'):
            self.dfa_canvas.delete('all')
        
        # Clear DFA display
        if hasattr(self, 'dfa_text'):
            self.dfa_text.delete('1.0', 'end')
        if hasattr(self, 'dfa_table'):
            self.dfa_table.delete(*self.dfa_table.get_children())
        
        self.refresh_all()

    def load_sample(self):
        self.manager.load_sample_data()
        self.refresh_all()

    def add_epsilon(self):
        """Add epsilon symbol to NFA"""
        try:
            self.manager.get_current_automaton().add_symbol('ε')
            self.refresh_all()
        except Exception as e:
            messagebox.showerror('Error', str(e))
    
    def convert_nfa_to_dfa(self):
        """Convert NFA to DFA and display results"""
        if self.mode_var.get() != 'NFA':
            messagebox.showwarning('Mode Error', 'Switch to NFA mode to convert to DFA')
            return
        
        if not self.manager.nfa.states:
            messagebox.showwarning('Empty NFA', 'NFA is empty. Add states and transitions first.')
            return
        
        success, message = self.manager.convert_to_dfa()
        if success:
            # Update DFA display
            self.dfa_text.delete('1.0', 'end')
            self.dfa_text.insert('1.0', self.manager.dfa.formal_definition())
            self._fill_table(self.dfa_table, *self.manager.dfa.transition_table())
            
            # Clear and render DFA diagram
            self.dfa_canvas.delete('all')
            self.render_dfa_diagram()
            
            # Switch to DFA tab to show results
            self.display_notebook.select(1)
            messagebox.showinfo('Success', message)
        else:
            messagebox.showerror('Conversion Error', message)
    
    def render_dfa_diagram(self):
        """Render the converted DFA diagram"""
        self.dfa_canvas.delete('all')
        if not hasattr(self, 'dfa_renderer'):
            self.dfa_renderer = DiagramRenderer(self.dfa_canvas)
        self.dfa_renderer.render_nfa_diagram(self.manager.dfa)

    def test_current(self):
        input_str = self.input_entry.get().strip()
        accepted, result, trace = self.manager.simulate_current(input_str)
        
        self.sim_result_label.config(text=f'{self.manager.mode} Result: {result}')
        self.trace_text.delete('1.0', 'end')
        self.trace_text.insert('1.0', '\n'.join(trace))
    
    def test_dfa(self):
        if not self.manager.dfa.states:
            messagebox.showwarning('No DFA', 'No DFA available. Convert NFA to DFA first.')
            return
        
        input_str = self.input_entry.get().strip()
        accepted, result, trace = self.manager.simulate_dfa(input_str)
        
        self.sim_result_label.config(text=f'DFA Result: {result}')
        self.trace_text.delete('1.0', 'end')
        self.trace_text.insert('1.0', '\n'.join(trace))

    def render_diagram(self):
        current = self.manager.get_current_automaton()
        self.renderer.render_nfa_diagram(current)
    


    def refresh_all(self):
        """Refresh all UI elements"""
        current = self.manager.get_current_automaton()
        
        # Update listboxes
        self.states_listbox.delete(0, 'end')
        for s in current.states:
            self.states_listbox.insert('end', s)
        
        self.symbols_listbox.delete(0, 'end')
        for sym in current.symbols:
            self.symbols_listbox.insert('end', sym)
        
        # Update comboboxes
        self.trans_sym_combo['values'] = current.symbols
        self.trans_src_combo['values'] = current.states
        self.trans_tgt_combo['values'] = current.states
        
        # Update labels
        self.start_label.config(text=f'Start: {current.start}')
        self.final_label.config(text=f'Finals: {{{", ".join(sorted(current.finals))}}}')
        
        # Update current automaton display
        self.automaton_text.delete('1.0', 'end')
        self.automaton_text.insert('1.0', current.formal_definition())
        self._fill_table(self.automaton_table, *current.transition_table())
        
        # Update display tab title
        mode = self.manager.mode
        self.display_notebook.tab(0, text=f'Current Automaton ({mode})')

    def _fill_table(self, tree, header, rows):
        """Fill treeview table with data"""
        tree.delete(*tree.get_children())
        tree['columns'] = header
        tree['show'] = 'headings'
        
        for col in header:
            tree.heading(col, text=col)
            tree.column(col, width=60, anchor='center')
        
        for row in rows:
            tree.insert('', 'end', values=row)


if __name__ == '__main__':
    app = AutomataGUI()
    app.mainloop()