(function () {
  function createMinimap(options) {
    const { host, nodes, edges, panzoom, getWorldBounds } = options;
    const ns = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(ns, 'svg');
    const edgeLayer = document.createElementNS(ns, 'g');
    const nodeLayer = document.createElementNS(ns, 'g');
    const viewport = document.createElementNS(ns, 'rect');
    viewport.setAttribute('class', 'viewport');
    svg.appendChild(edgeLayer);
    svg.appendChild(nodeLayer);
    svg.appendChild(viewport);
    host.appendChild(svg);

    function renderStatic() {
      edgeLayer.innerHTML = '';
      nodeLayer.innerHTML = '';
      edges.forEach((edge) => {
        const line = document.createElementNS(ns, 'line');
        const from = nodes.find((item) => item.id === edge.from);
        const to = nodes.find((item) => item.id === edge.to);
        if (!from || !to) return;
        line.setAttribute('x1', String(from.x + from.w / 2));
        line.setAttribute('y1', String(from.y + from.h / 2));
        line.setAttribute('x2', String(to.x + to.w / 2));
        line.setAttribute('y2', String(to.y + to.h / 2));
        line.setAttribute('stroke', '#5978ad');
        line.setAttribute('stroke-width', '3');
        edgeLayer.appendChild(line);
      });
      nodes.forEach((node) => {
        const rect = document.createElementNS(ns, 'rect');
        rect.setAttribute('x', String(node.x));
        rect.setAttribute('y', String(node.y));
        rect.setAttribute('width', String(node.w));
        rect.setAttribute('height', String(node.h));
        rect.setAttribute('fill', '#38517b');
        rect.setAttribute('stroke', '#9db9e6');
        rect.setAttribute('stroke-width', '2');
        nodeLayer.appendChild(rect);
      });
      const bounds = getWorldBounds();
      svg.setAttribute('viewBox', `${bounds.x} ${bounds.y} ${bounds.w} ${bounds.h}`);
    }

    function updateViewport() {
      const bounds = getWorldBounds();
      const state = panzoom.state;
      const rect = options.svg.getBoundingClientRect();
      const left = (-state.x) / state.scale;
      const top = (-state.y) / state.scale;
      const width = rect.width / state.scale;
      const height = rect.height / state.scale;
      viewport.setAttribute('x', String(Math.max(bounds.x, left)));
      viewport.setAttribute('y', String(Math.max(bounds.y, top)));
      viewport.setAttribute('width', String(Math.min(bounds.w, width)));
      viewport.setAttribute('height', String(Math.min(bounds.h, height)));
    }

    host.addEventListener('click', (event) => {
      const point = svg.createSVGPoint();
      point.x = event.clientX;
      point.y = event.clientY;
      const ctm = svg.getScreenCTM();
      if (!ctm) return;
      const worldPoint = point.matrixTransform(ctm.inverse());
      panzoom.centerOn(worldPoint.x, worldPoint.y);
    });

    renderStatic();
    updateViewport();
    return { renderStatic, updateViewport };
  }

  window.UIUXFlowMinimap = { createMinimap };
})();
