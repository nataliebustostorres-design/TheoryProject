async function refreshAll() {
  const def = await eel.get_definition()();
  document.getElementById('definition').textContent = def;

  const table = await eel.get_transition_table()();
  const wrap = document.getElementById('tablewrap');
  wrap.innerHTML = '';
  if (table && table.header) {
    const tbl = document.createElement('table');
    const thead = document.createElement('thead');
    const thr = document.createElement('tr');
    table.header.forEach(h => { const th = document.createElement('th'); th.textContent = h; thr.appendChild(th); });
    thead.appendChild(thr);
    tbl.appendChild(thead);
    const tbody = document.createElement('tbody');
    table.rows.forEach(r => { const tr = document.createElement('tr'); r.forEach(c => { const td = document.createElement('td'); td.textContent = c; tr.appendChild(td); }); tbody.appendChild(tr); });
    tbl.appendChild(tbody);
    wrap.appendChild(tbl);
  }

  const mode = document.getElementById('diagramMode') ? document.getElementById('diagramMode').value : 'current';
  const b64 = await eel.render_png_base64_for(mode)();
  const img = document.getElementById('diagramImg');
  if (b64) {
    img.src = 'data:image/png;base64,' + b64;
  } else {
    img.src = '';
    img.alt = 'Graphviz not available or rendering failed';
  }
}

async function setup() {
  document.getElementById('addState').onclick = async () => {
    const v = document.getElementById('stateName').value.trim();
    if (!v) return alert('Enter state name');
    await eel.add_state(v)();
    document.getElementById('stateName').value = '';
    refreshAll();
  };
  document.getElementById('delState').onclick = async () => {
    const v = document.getElementById('stateName').value.trim();
    if (!v) return alert('Enter state name to delete');
    await eel.delete_state(v)();
    document.getElementById('stateName').value = '';
    refreshAll();
  };

  document.getElementById('addSym').onclick = async () => {
    const v = document.getElementById('symName').value.trim();
    if (!v) return alert('Enter symbol');
    await eel.add_symbol(v)();
    document.getElementById('symName').value = '';
    refreshAll();
  };
  document.getElementById('delSym').onclick = async () => {
    const v = document.getElementById('symName').value.trim();
    if (!v) return alert('Enter symbol to delete');
    await eel.delete_symbol(v)();
    document.getElementById('symName').value = '';
    refreshAll();
  };

  document.getElementById('addTrans').onclick = async () => {
    const src = document.getElementById('tSrc').value.trim();
    const s = document.getElementById('tSym').value.trim();
    const tgt = document.getElementById('tTgt').value.trim();
    if (!src || !s || !tgt) return alert('Provide src, sym, tgt');
    await eel.add_transition(src, s, tgt)();
    document.getElementById('tSrc').value = '';
    document.getElementById('tSym').value = '';
    document.getElementById('tTgt').value = '';
    refreshAll();
  };

  document.getElementById('delTrans').onclick = async () => {
    const src = document.getElementById('tSrc').value.trim();
    const s = document.getElementById('tSym').value.trim();
    const tgt = document.getElementById('tTgt').value.trim();
    if (!src || !s || !tgt) return alert('Provide src, sym, tgt');
    await eel.delete_transition(src, s, tgt)();
    document.getElementById('tSrc').value = '';
    document.getElementById('tSym').value = '';
    document.getElementById('tTgt').value = '';
    refreshAll();
  };

  document.getElementById('setStart').onclick = async () => {
    const v = document.getElementById('startState').value.trim();
    if (!v) return alert('Enter start state');
    await eel.set_start(v)();
    document.getElementById('startState').value = '';
    refreshAll();
  };

  document.getElementById('toggleFinal').onclick = async () => {
    const v = document.getElementById('finalState').value.trim();
    if (!v) return alert('Enter final state');
    await eel.toggle_final(v)();
    document.getElementById('finalState').value = '';
    refreshAll();
  };

  document.getElementById('loadSample').onclick = async () => { await eel.load_sample()(); refreshAll(); };
  document.getElementById('reset').onclick = async () => { await eel.reset_automaton()(); refreshAll(); };
  document.getElementById('convert').onclick = async () => {
    const r = await eel.convert_nfa_to_dfa()();
    try { alert(r[1]); } catch(e) { console.log('convert message', r); }
    // If conversion succeeded, reveal render controls and show DFA diagram
    if (r && r[0]) {
      const wrap = document.getElementById('diagramControlsWrap');
      if (wrap) wrap.classList.remove('hidden');
      const modeSelect = document.getElementById('diagramMode');
      if (modeSelect) modeSelect.value = 'DFA';
      await refreshDiagram();
      // Show the "Use DFA Table" button so user can switch the table view
      const useBtn = document.getElementById('useDfaTable');
      if (useBtn) useBtn.classList.remove('hidden');
    }
    refreshAll();
  };

  // Use DFA Table button: toggle between DFA and NFA table views
  const useDfaBtn = document.getElementById('useDfaTable');
  async function updateUseDfaButtonLabel() {
    try {
      const mode = await eel.get_mode()();
      if (mode && mode.toUpperCase() === 'DFA') {
        useDfaBtn.textContent = 'Use NFA Table';
      } else {
        useDfaBtn.textContent = 'Use DFA Table';
      }
    } catch (e) {
      // Fallback label
      if (useDfaBtn) useDfaBtn.textContent = 'Use DFA Table';
    }
  }

  if (useDfaBtn) {
    useDfaBtn.onclick = async () => {
      try {
        const current = (await eel.get_mode()() || 'NFA').toUpperCase();
        const target = current === 'DFA' ? 'NFA' : 'DFA';
        await eel.set_mode(target)();
        // Update button label to reflect new opposite action
        await updateUseDfaButtonLabel();
        // If switching to DFA, also reveal diagram controls and set diagram mode
        if (target === 'DFA') {
          const wrap = document.getElementById('diagramControlsWrap');
          if (wrap) wrap.classList.remove('hidden');
          const modeSelect = document.getElementById('diagramMode');
          if (modeSelect) modeSelect.value = 'DFA';
          await refreshDiagram();
        }
        // Refresh table to reflect chosen automaton
        refreshAll();
      } catch (e) {
        console.error('toggle useDfaTable failed', e);
      }
    };
    // Ensure label is correct at startup if button visible
    updateUseDfaButtonLabel().catch(()=>{});
  }

  document.getElementById('simCur').onclick = async () => {
    const s = document.getElementById('inputStr').value;
    const res = await eel.simulate_current(s)();
    renderSimResult(res);
  };
  document.getElementById('simDfa').onclick = async () => {
    const s = document.getElementById('inputStr').value;
    const res = await eel.simulate_dfa(s)();
    renderSimResult(res);
  };

  // Diagram controls: refresh button and mode selector
  const diagramMode = document.getElementById('diagramMode');
  const refreshBtn = document.getElementById('refreshDiagram');
  if (refreshBtn) refreshBtn.onclick = refreshDiagram;
  if (diagramMode) diagramMode.onchange = refreshDiagram;

  // On load, detect if DFA is available so the Use DFA Table button appears
  try {
    const hasDfa = await eel.is_dfa_available()();
    if (hasDfa) {
      const useBtn2 = document.getElementById('useDfaTable');
      if (useBtn2) useBtn2.classList.remove('hidden');
    }
  } catch(e) { console.warn('is_dfa_available failed', e); }

  refreshAll();
}

async function refreshDiagram() {
  const mode = document.getElementById('diagramMode') ? document.getElementById('diagramMode').value : 'current';
  const b64 = await eel.render_png_base64_for(mode)();
  const img = document.getElementById('diagramImg');
  if (b64) {
    img.src = 'data:image/png;base64,' + b64;
    img.alt = 'diagram';
  } else {
    img.src = '';
    img.alt = 'Graphviz not available or rendering failed';
  }
}

window.addEventListener('DOMContentLoaded', setup);

function renderSimResult(res) {
  const resultDiv = document.getElementById('simResult');
  const stepsList = document.getElementById('simSteps');
  resultDiv.innerHTML = '';
  stepsList.innerHTML = '';
  if (!res) return;

  // res expected: { accepted: bool, message: str, steps: [str] }
  const accepted = !!res.accepted;
  const msg = res.message || (accepted ? 'ACCEPT' : 'REJECT');

  const span = document.createElement('span');
  span.textContent = msg;
  span.className = accepted ? 'sim-accepted' : 'sim-rejected';
  resultDiv.appendChild(span);

  if (Array.isArray(res.steps)) {
    res.steps.forEach(s => {
      const li = document.createElement('li');
      li.textContent = s;
      stepsList.appendChild(li);
    });
  }
}
