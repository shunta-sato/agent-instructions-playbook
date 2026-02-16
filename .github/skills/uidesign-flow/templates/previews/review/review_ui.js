(function () {
  function toElement(node) {
    if (!node) return null;
    if (node.nodeType === Node.ELEMENT_NODE) return node;
    if (node.nodeType === Node.TEXT_NODE) return node.parentElement;
    return null;
  }

  function closestFromNode(node, selector) {
    const el = toElement(node);
    if (!el) return null;
    return el.closest(selector);
  }

  function isTypingTarget(el) {
    if (!el) return false;
    const tag = el.tagName && el.tagName.toLowerCase();
    return tag === 'input' || tag === 'textarea' || tag === 'select' || el.isContentEditable;
  }

  function selectorFor(el) {
    if (!el) return '';
    if (el.dataset && el.dataset.reviewId) return `[data-review-id="${el.dataset.reviewId}"]`;
    const path = [];
    let node = el;
    while (node && node.nodeType === 1 && path.length < 5) {
      if (node.id) {
        path.unshift(`#${node.id}`);
        break;
      }
      let part = node.tagName.toLowerCase();
      if (node.classList.length) part += `.${Array.from(node.classList).slice(0, 2).join('.')}`;
      const parent = node.parentElement;
      if (parent) {
        const siblings = Array.from(parent.children).filter((child) => child.tagName === node.tagName);
        if (siblings.length > 1) {
          part += `:nth-of-type(${siblings.indexOf(node) + 1})`;
        }
      }
      path.unshift(part);
      node = node.parentElement;
    }
    return path.join(' > ');
  }

  function resolveTarget(root, anno) {
    const target = anno.target || {};
    if (target.data_review_id) {
      const byId = root.querySelector(`[data-review-id="${target.data_review_id}"]`);
      if (byId) return byId;
    }
    if (target.css_selector) {
      try {
        const byCss = root.querySelector(target.css_selector);
        if (byCss) return byCss;
      } catch (_) {
        return null;
      }
    }
    return null;
  }

  function rectToTarget(root, el) {
    const rootRect = root.getBoundingClientRect();
    const rect = el.getBoundingClientRect();
    const x = rect.left - rootRect.left;
    const y = rect.top - rootRect.top;
    return {
      rect: { x, y, w: rect.width, h: rect.height },
      pin: { x: x + rect.width / 2, y: y + rect.height / 2 }
    };
  }

  function stateHint(el) {
    if (!el) return 'default';
    if (el.matches(':disabled')) return 'disabled';
    if (el.classList.contains('error-state') || el.closest('.error')) return 'error';
    if (el.getAttribute('aria-busy') === 'true') return 'loading';
    if (document.activeElement === el) return 'focus';
    return 'default';
  }

  function byUpdatedDesc(a, b) {
    return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
  }

  function createPanel() {
    const wrap = document.createElement('aside');
    wrap.className = 'rv-panel';
    wrap.innerHTML = `
      <div class="rv-panel-head">
        <strong>Review</strong>
        <button class="btn" type="button" data-rv-close>Close</button>
      </div>
      <div class="rv-tabs">
        <button class="rv-tab is-active" type="button" data-rv-tab="add">Add</button>
        <button class="rv-tab" type="button" data-rv-tab="list">List</button>
      </div>
      <div class="rv-storage-warning" data-rv-storage-warning hidden>localStorage が使えないためメモリ保持のみです（リロードで消えます）。</div>
      <div data-rv-pane="add">
        <p class="rv-help" data-rv-help>Review ON にして要素をクリックすると追加できます。</p>
        <label class="label" for="rv-comment">Comment</label>
        <textarea id="rv-comment" class="rv-input" rows="5"></textarea>
        <div class="rv-row">
          <label class="label">Severity
            <select class="toolbar-select" data-rv-severity>
              <option value="blocker">blocker</option><option value="should" selected>should</option><option value="nice">nice</option>
            </select>
          </label>
          <label class="label">Status
            <select class="toolbar-select" data-rv-status><option value="open">open</option><option value="resolved">resolved</option></select>
          </label>
        </div>
        <div class="rv-row">
          <button class="btn btn-primary" type="button" data-rv-save>Save</button>
          <button class="btn" type="button" data-rv-cancel>Cancel</button>
          <button class="btn" type="button" data-rv-resolve hidden>Resolve</button>
          <button class="btn btn-danger" type="button" data-rv-delete hidden>Delete</button>
        </div>
      </div>
      <div data-rv-pane="list" hidden>
        <div class="rv-row rv-filters">
          <select class="toolbar-select" data-rv-filter-page><option value="this">This page</option><option value="all">All pages</option></select>
          <select class="toolbar-select" data-rv-filter-status><option value="all">All</option><option value="open">Open</option><option value="resolved">Resolved</option></select>
          <input class="rv-input" data-rv-filter-query placeholder="Search" />
        </div>
        <ol class="rv-list" data-rv-list></ol>
      </div>
      <div class="rv-copy-fallback" data-rv-copy-fallback hidden>
        <p class="p">Copy に失敗しました。手でコピーしてください。</p>
        <textarea class="rv-input" rows="8" data-rv-copy-text></textarea>
      </div>`;
    document.body.appendChild(wrap);
    return wrap;
  }

  document.addEventListener('DOMContentLoaded', function () {
    if (!window.UIDesignReviewStore || !window.UIDesignReviewExport) return;
    const store = window.UIDesignReviewStore.createStore();
    const exp = window.UIDesignReviewExport;
    const root = document.querySelector('[data-review-root]');
    const reviewToggle = document.getElementById('review-toggle');
    const exportBtn = document.getElementById('review-export-button');
    const exportMenu = document.getElementById('review-export-menu');
    const importInput = document.getElementById('review-import-input');
    const importBtn = document.getElementById('review-import-button');
    if (!root || !reviewToggle || !exportBtn || !exportMenu || !importInput || !importBtn) return;

    const panel = createPanel();
    const ui = store.loadUiState();
    let annotations = store.loadAll();
    let reviewOn = !!ui.reviewOn;
    let draft = null;
    let editId = null;
    let relinkId = null;

    const pinLayer = document.createElement('div');
    pinLayer.className = 'rv-pin-layer';
    root.appendChild(pinLayer);

    const reviewHint = document.createElement('div');
    reviewHint.className = 'rv-onboarding';
    reviewHint.textContent = 'Review ON: 要素をクリックしてコメント追加。Esc でキャンセル。';
    root.appendChild(reviewHint);

    const fileWarn = document.createElement('span');
    fileWarn.className = 'rv-file-warning';
    fileWarn.textContent = 'file:// ではコピーが不安定です。http://localhost で開いてください（例: python -m http.server 8000）。';
    if (location.protocol === 'file:') {
      const toolbarControls = document.querySelector('.toolbar-controls');
      if (toolbarControls) {
        toolbarControls.appendChild(fileWarn);
      }
    }

    const badge = document.createElement('span');
    badge.className = 'rv-badge';
    reviewToggle.appendChild(badge);

    const warning = panel.querySelector('[data-rv-storage-warning]');
    warning.hidden = store.isStorageAvailable();

    function saveUi() {
      ui.reviewOn = reviewOn;
      ui.panelOpen = panel.classList.contains('is-open');
      ui.filters = {
        page: panel.querySelector('[data-rv-filter-page]').value,
        status: panel.querySelector('[data-rv-filter-status]').value,
        query: panel.querySelector('[data-rv-filter-query]').value
      };
      store.saveUiState(ui);
    }

    function showPane(name) {
      panel.querySelectorAll('[data-rv-pane]').forEach((pane) => {
        pane.hidden = pane.getAttribute('data-rv-pane') !== name;
      });
      panel.querySelectorAll('.rv-tab').forEach((tab) => tab.classList.toggle('is-active', tab.dataset.rvTab === name));
    }

    function openPanel(tab) {
      panel.classList.add('is-open');
      showPane(tab || 'list');
      saveUi();
    }

    function closePanel() {
      panel.classList.remove('is-open');
      saveUi();
    }

    function applyFilters(list) {
      const fPage = panel.querySelector('[data-rv-filter-page]').value;
      const fStatus = panel.querySelector('[data-rv-filter-status]').value;
      const query = panel.querySelector('[data-rv-filter-query]').value.trim().toLowerCase();
      return list.filter((item) => {
        if (fPage === 'this' && item.page !== store.pagePath()) return false;
        if (fStatus !== 'all' && item.status !== fStatus) return false;
        if (!query) return true;
        const label = `${(item.body && item.body.text) || ''} ${(item.target && (item.target.data_review_id || item.target.css_selector)) || ''}`.toLowerCase();
        return label.includes(query);
      });
    }

    function sorted(list) {
      const open = list.filter((a) => a.status === 'open').sort(byUpdatedDesc);
      const resolved = list.filter((a) => a.status === 'resolved').sort(byUpdatedDesc);
      return open.concat(resolved);
    }

    function renderPins() {
      pinLayer.innerHTML = '';
      sorted(annotations).forEach((anno, idx) => {
        const targetEl = resolveTarget(root, anno);
        const pos = targetEl ? rectToTarget(root, targetEl).pin : (anno.target && anno.target.pin);
        if (!pos) return;
        const pin = document.createElement('button');
        pin.className = `rv-pin ${anno.status === 'resolved' ? 'is-resolved' : ''}`;
        pin.type = 'button';
        pin.style.left = `${pos.x}px`;
        pin.style.top = `${pos.y}px`;
        pin.textContent = String(idx + 1);
        pin.title = anno.id;
        pin.addEventListener('click', function (e) {
          e.stopPropagation();
          openEditor(anno.id);
        });
        pinLayer.appendChild(pin);
      });
    }

    function flashTarget(el) {
      if (!el) return;
      el.classList.add('rv-target-flash');
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      window.setTimeout(() => el.classList.remove('rv-target-flash'), 800);
    }

    function renderList() {
      const listNode = panel.querySelector('[data-rv-list]');
      listNode.innerHTML = '';
      sorted(applyFilters(annotations)).forEach((anno) => {
        const item = document.createElement('li');
        const linked = !!resolveTarget(root, anno);
        item.className = 'rv-item';
        item.innerHTML = `<button type="button" class="rv-item-open">[${anno.id}] ${anno.body.text || '(empty)'}<br><small>${anno.page} / ${anno.status}${linked ? '' : ' / Unlinked'}</small></button>`;
        item.querySelector('.rv-item-open').addEventListener('click', function () {
          const targetEl = resolveTarget(root, anno);
          if (targetEl) flashTarget(targetEl);
          openEditor(anno.id);
        });
        if (!linked) {
          const relink = document.createElement('button');
          relink.type = 'button';
          relink.className = 'btn';
          relink.textContent = 'Relink';
          relink.addEventListener('click', function () {
            relinkId = anno.id;
            reviewOn = true;
            syncReviewState();
            openPanel('add');
            panel.querySelector('[data-rv-help]').textContent = 'Relink: 次にクリックした要素へ付け替えます。';
          });
          item.appendChild(relink);
        }
        listNode.appendChild(item);
      });
      if (!listNode.children.length) listNode.innerHTML = '<li class="rv-item">No annotations</li>';
    }

    function syncReviewState() {
      document.body.classList.toggle('rv-review-mode', reviewOn);
      reviewToggle.setAttribute('aria-pressed', String(reviewOn));
      reviewToggle.classList.toggle('rv-toggle-on', reviewOn);
      reviewHint.classList.toggle('is-visible', reviewOn);
      badge.textContent = String(annotations.filter((a) => a.status === 'open').length);
      badge.hidden = !reviewOn;
      saveUi();
    }

    function nextAnnoId() {
      let max = 0;
      annotations.forEach((item) => {
        const m = String(item.id || '').match(/anno-(\d+)/);
        if (m) max = Math.max(max, Number(m[1]));
      });
      return `anno-${String(max + 1).padStart(4, '0')}`;
    }

    function clearForm() {
      draft = null;
      editId = null;
      panel.querySelector('#rv-comment').value = '';
      panel.querySelector('[data-rv-severity]').value = 'should';
      panel.querySelector('[data-rv-status]').value = 'open';
      panel.querySelector('[data-rv-delete]').hidden = true;
      panel.querySelector('[data-rv-resolve]').hidden = true;
      panel.querySelector('[data-rv-help]').textContent = 'Review ON にして要素をクリックすると追加できます。';
    }

    function openEditor(id) {
      const anno = annotations.find((item) => item.id === id);
      if (!anno) return;
      editId = id;
      draft = JSON.parse(JSON.stringify(anno));
      panel.querySelector('#rv-comment').value = (draft.body && draft.body.text) || '';
      panel.querySelector('[data-rv-severity]').value = draft.severity;
      panel.querySelector('[data-rv-status]').value = draft.status;
      panel.querySelector('[data-rv-delete]').hidden = false;
      panel.querySelector('[data-rv-resolve]').hidden = false;
      panel.querySelector('[data-rv-resolve]').textContent = draft.status === 'resolved' ? 'Unresolve' : 'Resolve';
      openPanel('add');
    }

    function saveCurrent() {
      if (!draft) return;
      draft.body.text = panel.querySelector('#rv-comment').value.trim();
      draft.severity = panel.querySelector('[data-rv-severity]').value;
      draft.status = panel.querySelector('[data-rv-status]').value;
      draft.updated_at = new Date().toISOString();
      if (!draft.body.text) return;
      if (editId) {
        annotations = annotations.map((item) => (item.id === editId ? draft : item));
      } else {
        annotations.push(draft);
      }
      store.saveAll(annotations);
      renderList();
      renderPins();
      syncReviewState();
      clearForm();
      openPanel('list');
    }

    root.addEventListener('mouseover', function (event) {
      if (!reviewOn) return;
      const el = toElement(event.target);
      if (!el || closestFromNode(el, '.rv-pin-layer')) return;
      document.querySelectorAll('.rv-hover').forEach((n) => n.classList.remove('rv-hover'));
      el.classList.add('rv-hover');
    });

    root.addEventListener('click', function (event) {
      if (!reviewOn) return;
      if (closestFromNode(event.target, '.rv-pin')) return;
      const el = toElement(event.target);
      if (!el || closestFromNode(el, '.toolbar') || closestFromNode(el, '.rv-panel')) return;
      event.preventDefault();
      const page = store.pagePath();
      const coords = rectToTarget(root, el);
      const target = {
        data_review_id: el.dataset && el.dataset.reviewId,
        css_selector: selectorFor(el),
        rect: coords.rect,
        pin: coords.pin
      };

      if (relinkId) {
        annotations = annotations.map((item) => (item.id === relinkId ? { ...item, target, updated_at: new Date().toISOString() } : item));
        relinkId = null;
        store.saveAll(annotations);
        renderPins();
        renderList();
        return;
      }

      clearForm();
      draft = {
        id: nextAnnoId(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        status: 'open',
        severity: 'should',
        page,
        body: { text: '' },
        target,
        ui_context: {
          theme: document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light',
          viewport: { width: root.clientWidth, height: root.clientHeight },
          state_hint: stateHint(el)
        }
      };
      openPanel('add');
      panel.querySelector('[data-rv-help]').textContent = 'コメントを入力して Save してください。';
      panel.querySelector('#rv-comment').focus();
    });

    reviewToggle.addEventListener('click', function () {
      reviewOn = !reviewOn;
      syncReviewState();
      if (reviewOn) openPanel('list');
    });

    panel.querySelector('[data-rv-close]').addEventListener('click', closePanel);
    panel.querySelectorAll('.rv-tab').forEach((tab) => tab.addEventListener('click', () => showPane(tab.dataset.rvTab)));
    panel.querySelector('[data-rv-save]').addEventListener('click', saveCurrent);
    panel.querySelector('[data-rv-cancel]').addEventListener('click', function () {
      clearForm();
      showPane('list');
    });
    panel.querySelector('[data-rv-delete]').addEventListener('click', function () {
      if (!editId) return;
      if (!window.confirm('Delete this annotation?')) return;
      annotations = annotations.filter((item) => item.id !== editId);
      store.saveAll(annotations);
      clearForm();
      renderPins();
      renderList();
      showPane('list');
      syncReviewState();
    });
    panel.querySelector('[data-rv-resolve]').addEventListener('click', function () {
      if (!draft) return;
      draft.status = draft.status === 'resolved' ? 'open' : 'resolved';
      panel.querySelector('[data-rv-status]').value = draft.status;
      panel.querySelector('[data-rv-resolve]').textContent = draft.status === 'resolved' ? 'Unresolve' : 'Resolve';
    });
    panel.querySelectorAll('[data-rv-filter-page],[data-rv-filter-status],[data-rv-filter-query]').forEach((el) => {
      el.addEventListener('input', function () {
        renderList();
        saveUi();
      });
      el.addEventListener('change', function () {
        renderList();
        saveUi();
      });
    });

    exportBtn.addEventListener('click', function () {
      exportMenu.classList.toggle('is-open');
    });
    document.addEventListener('click', function (event) {
      if (!closestFromNode(event.target, '.rv-export')) exportMenu.classList.remove('is-open');
    });
    exportMenu.querySelector('[data-export-json]').addEventListener('click', function () {
      exp.download('annotations.json', JSON.stringify(exp.buildJson({ packId: store.packId, version: store.version, annotations }), null, 2), 'application/json');
    });
    exportMenu.querySelector('[data-export-markdown]').addEventListener('click', function () {
      exp.download('review_notes.generated.md', exp.buildMarkdown(annotations), 'text/markdown');
    });
    exportMenu.querySelector('[data-copy-markdown]').addEventListener('click', async function () {
      const md = exp.buildMarkdown(annotations);
      try {
        await exp.copyMarkdown(md);
        panel.querySelector('[data-rv-copy-fallback]').hidden = true;
      } catch (_) {
        panel.querySelector('[data-rv-copy-fallback]').hidden = false;
        panel.querySelector('[data-rv-copy-text]').value = md;
        openPanel('add');
      }
    });

    importBtn.addEventListener('click', () => importInput.click());
    importInput.addEventListener('change', async function () {
      const file = importInput.files && importInput.files[0];
      if (!file) return;
      try {
        const incoming = await exp.importJsonFile(file);
        const mode = window.confirm('OK: Replace / Cancel: Merge') ? 'replace' : 'merge';
        annotations = mode === 'replace' ? store.replaceAll(incoming) : store.mergeAll(incoming);
        renderPins();
        renderList();
        syncReviewState();
      } catch (error) {
        window.alert(`Import failed: ${error.message}`);
      }
      importInput.value = '';
    });

    document.addEventListener('keydown', function (event) {
      if (event.key.toLowerCase() === 'r' && !isTypingTarget(event.target)) {
        reviewOn = !reviewOn;
        syncReviewState();
      }
      if (event.key === 'Escape') {
        if (panel.classList.contains('is-open')) {
          clearForm();
          closePanel();
        }
      }
      if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        if (document.activeElement && panel.contains(document.activeElement)) {
          saveCurrent();
        }
      }
    });

    if (ui.filters) {
      panel.querySelector('[data-rv-filter-page]').value = ui.filters.page || 'this';
      panel.querySelector('[data-rv-filter-status]').value = ui.filters.status || 'all';
      panel.querySelector('[data-rv-filter-query]').value = ui.filters.query || '';
    }
    if (ui.panelOpen) panel.classList.add('is-open');
    syncReviewState();
    renderPins();
    renderList();
  });
})();
