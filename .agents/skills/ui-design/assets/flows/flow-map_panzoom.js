(function () {
  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function createPanZoom(options) {
    const { svg, world, onChange } = options;
    const state = { x: 0, y: 0, scale: 1, minScale: 0.3, maxScale: 2.5 };
    const pointers = new Map();
    let drag = null;
    let pinch = null;

    function apply() {
      world.setAttribute('transform', `translate(${state.x} ${state.y}) scale(${state.scale})`);
      window.dispatchEvent(new CustomEvent('rv:viewportChanged'));
      if (onChange) onChange(state);
    }

    function toLocal(clientX, clientY) {
      const rect = svg.getBoundingClientRect();
      return { x: clientX - rect.left, y: clientY - rect.top };
    }

    function zoomAt(clientX, clientY, factor) {
      const point = toLocal(clientX, clientY);
      const nextScale = clamp(state.scale * factor, state.minScale, state.maxScale);
      const ratio = nextScale / state.scale;
      state.x = point.x - (point.x - state.x) * ratio;
      state.y = point.y - (point.y - state.y) * ratio;
      state.scale = nextScale;
      apply();
    }

    svg.addEventListener('pointerdown', (event) => {
      svg.setPointerCapture(event.pointerId);
      pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
      if (pointers.size === 1) {
        drag = { x: event.clientX, y: event.clientY, baseX: state.x, baseY: state.y };
      }
      if (pointers.size === 2) {
        const pts = Array.from(pointers.values());
        pinch = {
          distance: Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y),
          scale: state.scale
        };
      }
    });

    svg.addEventListener('pointermove', (event) => {
      if (!pointers.has(event.pointerId)) return;
      pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
      if (pointers.size === 1 && drag) {
        state.x = drag.baseX + (event.clientX - drag.x);
        state.y = drag.baseY + (event.clientY - drag.y);
        apply();
      }
      if (pointers.size === 2 && pinch) {
        const pts = Array.from(pointers.values());
        const dist = Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y);
        const center = { x: (pts[0].x + pts[1].x) / 2, y: (pts[0].y + pts[1].y) / 2 };
        const desired = clamp(pinch.scale * (dist / Math.max(1, pinch.distance)), state.minScale, state.maxScale);
        const factor = desired / state.scale;
        zoomAt(center.x, center.y, factor);
      }
    });

    function clearPointer(event) {
      pointers.delete(event.pointerId);
      if (pointers.size === 0) {
        drag = null;
        pinch = null;
      }
    }

    svg.addEventListener('pointerup', clearPointer);
    svg.addEventListener('pointercancel', clearPointer);

    svg.addEventListener('wheel', (event) => {
      event.preventDefault();
      const pixelLike = event.deltaMode === WheelEvent.DOM_DELTA_PIXEL;
      if (pixelLike && !event.ctrlKey) {
        state.x -= event.deltaX;
        state.y -= event.deltaY;
        apply();
        return;
      }
      const direction = event.deltaY > 0 ? 0.9 : 1.1;
      zoomAt(event.clientX, event.clientY, direction);
    }, { passive: false });

    function fitTo(bounds, padding) {
      const rect = svg.getBoundingClientRect();
      const p = padding || 40;
      const sx = (rect.width - p * 2) / Math.max(1, bounds.w);
      const sy = (rect.height - p * 2) / Math.max(1, bounds.h);
      state.scale = clamp(Math.min(sx, sy), state.minScale, state.maxScale);
      state.x = rect.width / 2 - (bounds.x + bounds.w / 2) * state.scale;
      state.y = rect.height / 2 - (bounds.y + bounds.h / 2) * state.scale;
      apply();
    }

    function centerOn(worldX, worldY) {
      const rect = svg.getBoundingClientRect();
      state.x = rect.width / 2 - worldX * state.scale;
      state.y = rect.height / 2 - worldY * state.scale;
      apply();
    }

    return { state, apply, zoomAt, fitTo, centerOn };
  }

  window.UIUXFlowPanZoom = { createPanZoom };
})();
