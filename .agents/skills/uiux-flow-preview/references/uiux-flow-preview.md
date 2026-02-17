# uiux-flow-preview reference

## Goal

Provide a map-style transition preview that keeps orientation in large screen graphs:

- overview + detail (minimap + main canvas)
- pointer/touch pan and zoom
- focus-based transition walkthrough (`Next` / `Prev` / `Enter` / `Back`)
- review annotations on node/edge/UI controls via stable `data-review-id`

## Required output files

Under `uiux/<pack>/previews/`:

- `flow-map.html`
- `flow-map.css`
- `flow-map.js`
- `flow-map_panzoom.js`
- `flow-map_focus.js`
- `flow-map_minimap.js`
- `review/review.css`
- `review/review_store.js`
- `review/review_export.js`
- `review/review_ui.js`

## Data model expectations

Read from `window.UIUX_SPEC`:

- `information_architecture.screens[]` (`id`, `name`, `goal`)
- `information_architecture.navigation[]` (`from`, `to`, optional `trigger`)
- `information_architecture.decision_points[]` (`screen`, `options`)

## Interaction requirements

- Pan: pointer drag (mouse/touch/pen)
- Zoom: wheel + pinch (2-pointer distance)
- Zoom anchor: cursor/pinch midpoint
- Minimap: show world extent + viewport rectangle, click to center
- Focus panel: selected screen details, outgoing/incoming lists, decision points
- Keyboard: `Enter`, `Backspace` (or `Alt+ArrowLeft`), plus traversal helpers

## Review integration

- Node: `data-review-id="flow_node_<screenId>"`
- Edge: `data-review-id="flow_edge_<from>__<to>__<trigger>"` (`trigger` omitted when absent)
- Control buttons: include stable `data-review-id` values
- On every viewport transform update, dispatch:

```js
window.dispatchEvent(new CustomEvent('rv:viewportChanged'));
```

`review_ui.js` listens and rerenders pins via `requestAnimationFrame`.
