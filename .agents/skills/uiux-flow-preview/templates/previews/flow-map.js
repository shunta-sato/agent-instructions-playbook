(function () {
  const SVG_NS = 'http://www.w3.org/2000/svg';

  function safeId(value) {
    return String(value || '').trim().replace(/[^a-zA-Z0-9_-]+/g, '_');
  }

  function edgeReviewId(edge) {
    const base = `flow_edge_${safeId(edge.from)}__${safeId(edge.to)}`;
    return edge.trigger ? `${base}__${safeId(edge.trigger)}` : base;
  }

  function buildLayout(spec) {
    const screens = (((spec || {}).information_architecture || {}).screens || []).map((screen, index) => {
      const col = index % 4;
      const row = Math.floor(index / 4);
      return { ...screen, x: 120 + col * 300, y: 120 + row * 220, w: 180, h: 90 };
    });
    const edges = (((spec || {}).information_architecture || {}).navigation || []).map((edge) => ({ ...edge }));
    const decisionPoints = (((spec || {}).information_architecture || {}).decision_points || []).map((item) => ({ ...item }));
    return { screens, edges, decisionPoints };
  }

  function worldBounds(nodes) {
    if (!nodes.length) return { x: 0, y: 0, w: 800, h: 600 };
    const minX = Math.min(...nodes.map((n) => n.x)) - 80;
    const minY = Math.min(...nodes.map((n) => n.y)) - 80;
    const maxX = Math.max(...nodes.map((n) => n.x + n.w)) + 80;
    const maxY = Math.max(...nodes.map((n) => n.y + n.h)) + 80;
    return { x: minX, y: minY, w: maxX - minX, h: maxY - minY };
  }

  function createNode(node, focus) {
    const g = document.createElementNS(SVG_NS, 'g');
    g.setAttribute('class', 'flow-node');
    g.setAttribute('transform', `translate(${node.x} ${node.y})`);
    g.setAttribute('data-review-id', `flow_node_${safeId(node.id)}`);
    const rect = document.createElementNS(SVG_NS, 'rect');
    rect.setAttribute('rx', '14');
    rect.setAttribute('ry', '14');
    rect.setAttribute('width', String(node.w));
    rect.setAttribute('height', String(node.h));
    const title = document.createElementNS(SVG_NS, 'text');
    title.setAttribute('x', '12');
    title.setAttribute('y', '34');
    title.textContent = `${node.id} ${node.name ? `- ${node.name}` : ''}`;
    g.appendChild(rect);
    g.appendChild(title);
    g.addEventListener('click', () => focus(node.id));
    node.el = g;
    return g;
  }

  function createEdge(edge, nodes) {
    const from = nodes.find((n) => n.id === edge.from);
    const to = nodes.find((n) => n.id === edge.to);
    if (!from || !to) return null;
    const g = document.createElementNS(SVG_NS, 'g');
    g.setAttribute('class', 'flow-edge');
    g.setAttribute('data-review-id', edgeReviewId(edge));
    const path = document.createElementNS(SVG_NS, 'path');
    const sx = from.x + from.w;
    const sy = from.y + from.h / 2;
    const tx = to.x;
    const ty = to.y + to.h / 2;
    const cx = (sx + tx) / 2;
    path.setAttribute('d', `M ${sx} ${sy} C ${cx} ${sy}, ${cx} ${ty}, ${tx} ${ty}`);
    g.appendChild(path);
    if (edge.trigger) {
      const label = document.createElementNS(SVG_NS, 'text');
      label.setAttribute('x', String(cx));
      label.setAttribute('y', String((sy + ty) / 2 - 8));
      label.textContent = edge.trigger;
      g.appendChild(label);
    }
    edge.el = g;
    return g;
  }

  document.addEventListener('DOMContentLoaded', () => {
    const spec = window.UIUX_SPEC || {};
    const svg = document.querySelector('.flow-canvas');
    const world = document.querySelector('[data-world]');
    const nodeLayer = document.querySelector('[data-node-layer]');
    const edgeLayer = document.querySelector('[data-edge-layer]');
    const panel = document.querySelector('.side-panel');
    const minimapHost = document.querySelector('[data-minimap]');
    if (!svg || !world || !nodeLayer || !edgeLayer || !panel || !minimapHost) return;

    const { screens, edges, decisionPoints } = buildLayout(spec);
    const bounds = worldBounds(screens);
    const panzoom = window.UIUXFlowPanZoom.createPanZoom({ svg, world });
    const focus = window.UIUXFlowFocus.createFocusController({ nodes: screens, edges, panel, decisionPoints, panzoom });

    edges.forEach((edge) => {
      const el = createEdge(edge, screens);
      if (el) edgeLayer.appendChild(el);
    });
    screens.forEach((node) => {
      nodeLayer.appendChild(createNode(node, focus.focusNode));
    });

    const minimap = window.UIUXFlowMinimap.createMinimap({
      host: minimapHost,
      svg,
      nodes: screens,
      edges,
      panzoom,
      getWorldBounds: () => bounds
    });

    const followButton = document.querySelector('[data-action="follow"]');
    let followOn = false;
    const actionHandlers = {
      'zoom-in': () => panzoom.zoomAt(window.innerWidth / 2, window.innerHeight / 2, 1.15),
      'zoom-out': () => panzoom.zoomAt(window.innerWidth / 2, window.innerHeight / 2, 0.87),
      fit: () => panzoom.fitTo(bounds),
      home: () => { panzoom.state.scale = 1; panzoom.state.x = 0; panzoom.state.y = 0; panzoom.apply(); },
      follow: () => {
        followOn = !followOn;
        followButton.setAttribute('aria-pressed', String(followOn));
        focus.setFollow(followOn);
      },
      next: () => focus.moveSelection(1),
      prev: () => focus.moveSelection(-1),
      go: () => focus.goSelected(),
      back: () => focus.back()
    };

    document.querySelectorAll('[data-action]').forEach((button) => {
      button.addEventListener('click', () => {
        const fn = actionHandlers[button.dataset.action];
        if (fn) fn();
      });
    });

    const search = document.getElementById('flow-search');
    search.addEventListener('input', () => {
      const q = search.value.trim().toLowerCase();
      screens.forEach((node) => {
        const hit = q && (`${node.id} ${node.name || ''}`).toLowerCase().includes(q);
        node.el.classList.toggle('search-hit', !!hit);
      });
      const exact = screens.find((node) => node.id.toLowerCase() === q || (node.name || '').toLowerCase() === q);
      if (exact) focus.focusNode(exact.id, { follow: true });
    });

    window.addEventListener('keydown', (event) => {
      if (event.key === 'Enter') {
        event.preventDefault();
        focus.goSelected();
      }
      if (event.key === 'Backspace' || (event.altKey && event.key === 'ArrowLeft')) {
        event.preventDefault();
        focus.back();
      }
    });

    window.addEventListener('resize', minimap.updateViewport);
    window.addEventListener('rv:viewportChanged', minimap.updateViewport);
    panzoom.fitTo(bounds);
  });
})();
