(function () {
  const VERSION = 2;
  const mem = new Map();

  function safeRead(key) {
    try {
      return window.localStorage.getItem(key);
    } catch (_) {
      return mem.get(key) || null;
    }
  }

  function safeWrite(key, value) {
    try {
      window.localStorage.setItem(key, value);
      return true;
    } catch (_) {
      mem.set(key, value);
      return false;
    }
  }

  function parseJSON(value, fallback) {
    if (!value) return fallback;
    try {
      return JSON.parse(value);
    } catch (_) {
      return fallback;
    }
  }

  function nowIso() {
    return new Date().toISOString();
  }

  function pagePath() {
    const raw = window.location.pathname || 'previews/index.html';
    return raw.replace(/^.*?(previews\/)/, 'previews/');
  }

  function derivePackId() {
    const text = document.body ? document.body.textContent || '' : '';
    const match = text.match(/uiux\/[0-9]{8}-[\w-]+/);
    if (match) return match[0];
    return (window.location.pathname || 'uidesign-pack').replace(/[^a-zA-Z0-9/_-]/g, '_');
  }

  function nextId(list) {
    let max = 0;
    list.forEach((item) => {
      const m = String(item.id || '').match(/anno-(\d+)/);
      if (m) max = Math.max(max, Number(m[1]));
    });
    return `anno-${String(max + 1).padStart(4, '0')}`;
  }

  function normalizeAnnotation(input, list) {
    const created = input.created_at || nowIso();
    return {
      id: input.id || nextId(list || []),
      created_at: created,
      updated_at: input.updated_at || created,
      status: input.status === 'resolved' ? 'resolved' : 'open',
      severity: ['blocker', 'should', 'nice'].includes(input.severity) ? input.severity : 'should',
      page: input.page || pagePath(),
      body: { text: (input.body && input.body.text) || '' },
      target: {
        data_review_id: input.target && input.target.data_review_id,
        css_selector: input.target && input.target.css_selector,
        rect: input.target && input.target.rect,
        pin: input.target && input.target.pin,
        text_quote: input.target && input.target.text_quote
      },
      ui_context: {
        theme: (input.ui_context && input.ui_context.theme) || 'light',
        viewport: input.ui_context && input.ui_context.viewport,
        state_hint: input.ui_context && input.ui_context.state_hint
      }
    };
  }

  function migrate(raw) {
    if (Array.isArray(raw)) {
      return raw.map((item) => normalizeAnnotation({
        id: item.id,
        created_at: item.createdAt,
        updated_at: item.createdAt,
        status: 'open',
        severity: 'should',
        page: item.page,
        body: { text: item.comment || '' },
        target: { css_selector: item.selector || item.element }
      }, raw));
    }
    const list = raw && Array.isArray(raw.annotations) ? raw.annotations : [];
    return list.map((item) => normalizeAnnotation(item, list));
  }

  function createStore() {
    const packId = derivePackId();
    const keyAll = `uidesign_review::${packId}::all`;
    const keyUi = `uidesign_review::${packId}::ui_state`;

    function loadAll() {
      return migrate(parseJSON(safeRead(keyAll), { annotations: [] }));
    }

    function saveAll(annotations) {
      return safeWrite(keyAll, JSON.stringify({ version: VERSION, annotations }, null, 2));
    }

    function loadUiState() {
      return parseJSON(safeRead(keyUi), {
        reviewOn: false,
        panelOpen: false,
        filters: { page: 'this', status: 'all', query: '' }
      });
    }

    function saveUiState(uiState) {
      return safeWrite(keyUi, JSON.stringify(uiState));
    }

    function replaceAll(items) {
      const normalized = (items || []).map((it) => normalizeAnnotation(it, items));
      saveAll(normalized);
      return normalized;
    }

    function mergeAll(items) {
      const curr = loadAll();
      const map = new Map(curr.map((item) => [item.id, item]));
      (items || []).forEach((item) => {
        const normalized = normalizeAnnotation(item, curr);
        map.set(normalized.id, normalized);
      });
      const merged = Array.from(map.values());
      saveAll(merged);
      return merged;
    }

    return {
      packId,
      version: VERSION,
      pagePath,
      loadAll,
      saveAll,
      loadUiState,
      saveUiState,
      replaceAll,
      mergeAll,
      isStorageAvailable: function () {
        try {
          const key = '__rv_probe__';
          localStorage.setItem(key, '1');
          localStorage.removeItem(key);
          return true;
        } catch (_) {
          return false;
        }
      }
    };
  }

  window.UIDesignReviewStore = { createStore };
})();
