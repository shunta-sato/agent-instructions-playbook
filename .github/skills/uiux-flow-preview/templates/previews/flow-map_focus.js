(function () {
  function createFocusController(ctx) {
    const { nodes, edges, panel, panzoom } = ctx;
    let focusedId = null;
    let selectedOutgoing = -1;
    let follow = false;
    const history = [];

    function edgeForNode(id) {
      return {
        outgoing: edges.filter((edge) => edge.from === id),
        incoming: edges.filter((edge) => edge.to === id)
      };
    }

    function syncClasses() {
      nodes.forEach((node) => {
        const connected = focusedId
          ? node.id === focusedId || edges.some((edge) => (edge.from === focusedId && edge.to === node.id) || (edge.to === focusedId && edge.from === node.id))
          : true;
        node.el.classList.toggle('is-focus', node.id === focusedId);
        node.el.classList.toggle('is-dim', !!focusedId && !connected);
      });
      edges.forEach((edge, index) => {
        const connected = focusedId ? edge.from === focusedId || edge.to === focusedId : true;
        const selected = focusedId && edge.from === focusedId && index === selectedOutgoing;
        edge.el.classList.toggle('is-focus', !!selected || (focusedId && connected));
        edge.el.classList.toggle('is-dim', !!focusedId && !connected);
      });
    }

    function renderPanel() {
      const title = panel.querySelector('[data-focus-title]');
      const goal = panel.querySelector('[data-focus-goal]');
      const outgoingList = panel.querySelector('[data-outgoing-list]');
      const incomingList = panel.querySelector('[data-incoming-list]');
      const decisionList = panel.querySelector('[data-decision-list]');
      outgoingList.innerHTML = '';
      incomingList.innerHTML = '';
      decisionList.innerHTML = '';

      const node = nodes.find((item) => item.id === focusedId);
      if (!node) {
        title.textContent = 'Select a screen node.';
        goal.textContent = '';
        return;
      }

      title.textContent = `Screen: ${node.id} / ${node.name || '(unnamed)'}`;
      goal.textContent = `Goal: ${node.goal || '-'}`;
      const relation = edgeForNode(node.id);

      relation.outgoing.forEach((edge, idx) => {
        const li = document.createElement('li');
        const trigger = edge.trigger ? `[${edge.trigger}] ` : '';
        li.innerHTML = `<button type="button" class="btn">${trigger}${edge.to}</button>`;
        li.querySelector('button').addEventListener('click', () => {
          selectedOutgoing = idx;
          syncClasses();
        });
        outgoingList.appendChild(li);
      });

      relation.incoming.forEach((edge) => {
        const li = document.createElement('li');
        li.textContent = `${edge.from} → ${node.id}`;
        incomingList.appendChild(li);
      });

      (ctx.decisionPoints || []).filter((item) => item.screen === node.id).forEach((point) => {
        const li = document.createElement('li');
        li.textContent = `${point.question || 'Decision'}: ${(point.options || []).join(' / ')}`;
        decisionList.appendChild(li);
      });
    }

    function focusNode(id, options) {
      if (!id || id === focusedId) return;
      if (focusedId) history.push(focusedId);
      focusedId = id;
      selectedOutgoing = 0;
      syncClasses();
      renderPanel();
      if (follow || (options && options.follow)) {
        const node = nodes.find((item) => item.id === id);
        if (node) panzoom.centerOn(node.x + node.w / 2, node.y + node.h / 2);
      }
    }

    function goSelected() {
      const relation = edgeForNode(focusedId).outgoing;
      if (!relation.length) return;
      const next = relation[Math.max(0, selectedOutgoing)] || relation[0];
      focusNode(next.to, { follow: true });
    }

    function moveSelection(step) {
      const relation = edgeForNode(focusedId).outgoing;
      if (!relation.length) return;
      selectedOutgoing = (selectedOutgoing + step + relation.length) % relation.length;
      syncClasses();
    }

    function back() {
      const prev = history.pop();
      if (!prev) return;
      focusedId = null;
      focusNode(prev, { follow: true });
    }

    return {
      focusNode,
      goSelected,
      moveSelection,
      back,
      setFollow(value) { follow = !!value; },
      getFocusedId() { return focusedId; }
    };
  }

  window.UIUXFlowFocus = { createFocusController };
})();
