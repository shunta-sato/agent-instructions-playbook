(function () {
  const STORAGE_KEY = 'uidesign_review_comments_v1';

  function loadComments() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    } catch (_) {
      return [];
    }
  }

  function saveComments(comments) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(comments)); } catch (_) {}
  }

  function toElementPath(element) {
    if (!element || !element.tagName) return 'unknown';
    if (element.id) return `${element.tagName.toLowerCase()}#${element.id}`;
    const classes = Array.from(element.classList || []).slice(0, 2).join('.');
    return classes ? `${element.tagName.toLowerCase()}.${classes}` : element.tagName.toLowerCase();
  }

  function inferState(element) {
    if (element.matches(':disabled')) return 'disabled';
    if (element.classList.contains('error-state')) return 'error';
    return 'default';
  }

  function toMarkdown(comments) {
    const lines = [
      '# UIDesign Review Notes (export)',
      '',
      '## Pinned feedback',
      ''
    ];

    if (!comments.length) {
      lines.push('- No comments yet.');
      return lines.join('\n');
    }

    comments.forEach((comment, index) => {
      lines.push(`### ${index + 1}. ${comment.page}`);
      lines.push(`- Page: ${comment.page}`);
      lines.push(`- Element: ${comment.element}`);
      lines.push(`- State: ${comment.state}`);
      lines.push(`- Change: ${comment.comment}`);
      lines.push(`- Reason: ${comment.reason || '(fill reason)'}`);
      lines.push('');
    });

    return lines.join('\n');
  }


  function createCommentId() {
    if (window.crypto && typeof window.crypto.randomUUID === 'function') {
      return window.crypto.randomUUID();
    }
    return `comment-${Date.now()}-${Math.floor(Math.random() * 1e6)}`;
  }

  function download(name, text, type) {
    const blob = new Blob([text], { type });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = name;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  function init() {
    const toggle = document.getElementById('reviewModeToggle');
    const exportJson = document.getElementById('exportReviewJson');
    const exportMarkdown = document.getElementById('exportReviewMarkdown');
    const board = document.getElementById('reviewBoard');
    const root = document.getElementById('deviceCanvas');
    if (!toggle || !exportJson || !exportMarkdown || !board || !root) return;

    const state = {
      active: false,
      comments: loadComments()
    };

    function render() {
      board.innerHTML = '';
      if (!state.comments.length) {
        board.innerHTML = '<p class="review-empty">No comments yet.</p>';
        return;
      }

      state.comments.slice().reverse().forEach((item) => {
        const card = document.createElement('article');
        card.className = 'review-item';
        card.innerHTML = `
          <div class="review-item-head"><strong>${item.page}</strong> / ${item.element}</div>
          <div class="review-item-meta">state: ${item.state}</div>
          <p>${item.comment}</p>
        `;
        board.appendChild(card);
      });
    }

    toggle.addEventListener('click', () => {
      state.active = !state.active;
      document.body.classList.toggle('review-mode', state.active);
      toggle.textContent = state.active ? 'Review: ON' : 'Review: OFF';
    });

    root.addEventListener('click', (event) => {
      if (!state.active) return;

      const target = event.target.closest('button, input, a, .card, .alert, .label, .p, .h1');
      if (!target) return;

      event.preventDefault();
      event.stopPropagation();

      const comment = window.prompt('Comment (Change):');
      if (!comment) return;
      const reason = window.prompt('Reason (optional):', '') || '';

      state.comments.push({
        id: createCommentId(),
        page: window.location.pathname.split('/').pop() || 'unknown',
        element: toElementPath(target),
        state: inferState(target),
        comment,
        reason,
        annotation: {
          type: 'Annotation',
          body: { type: 'TextualBody', purpose: 'commenting', value: comment },
          target: { source: window.location.href, selector: { type: 'CssSelector', value: toElementPath(target) } }
        },
        createdAt: new Date().toISOString()
      });

      saveComments(state.comments);
      render();
    });

    exportJson.addEventListener('click', () => {
      download('review-comments.json', JSON.stringify(state.comments, null, 2), 'application/json');
    });

    exportMarkdown.addEventListener('click', () => {
      download('review_notes.md', toMarkdown(state.comments), 'text/markdown');
    });

    render();
  }

  window.UIDesignReview = { init };
})();
