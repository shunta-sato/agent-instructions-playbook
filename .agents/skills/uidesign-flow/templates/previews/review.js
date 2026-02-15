(function () {
  const STORAGE_KEY = 'uidesign_review_comments_v1';

  function loadComments() {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch (_) {
      return [];
    }
  }

  function saveComments(comments) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(comments));
    } catch (_) {
      // Ignore storage errors.
    }
  }

  function selectorFor(element) {
    if (element.id) return `#${element.id}`;
    const classes = Array.from(element.classList || []).slice(0, 2).join('.');
    return classes ? `${element.tagName.toLowerCase()}.${classes}` : element.tagName.toLowerCase();
  }

  function deriveState(element) {
    if (element.matches(':disabled')) return 'disabled';
    if (element.classList.contains('error-state')) return 'error';
    if (element.getAttribute('aria-busy') === 'true') return 'loading';
    return 'default';
  }

  function toMarkdown(comments) {
    const lines = ['# UIDesign Review Notes (export)', '', '## Comments'];
    comments.forEach((item, index) => {
      lines.push(`${index + 1}. Page: ${item.page}`);
      lines.push(`   - Element: ${item.element}`);
      lines.push(`   - State: ${item.state}`);
      lines.push(`   - Change: ${item.comment}`);
      lines.push(`   - Reason: ${item.reason || '(fill reason)'}`);
    });
    if (!comments.length) {
      lines.push('- (No comments yet)');
    }
    return lines.join('\n');
  }

  function downloadFile(filename, content, type) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  document.addEventListener('DOMContentLoaded', function () {
    const reviewToggle = document.getElementById('review-toggle');
    const exportJsonButton = document.getElementById('export-json');
    const exportMarkdownButton = document.getElementById('export-markdown');
    const clearReviewButton = document.getElementById('clear-review');
    const reviewList = document.getElementById('review-list');
    const reviewRoot = document.querySelector('[data-review-root]');
    if (!reviewToggle || !reviewList || !reviewRoot) return;

    let comments = loadComments();
    let reviewMode = false;

    function renderList() {
      reviewList.innerHTML = '';
      if (!comments.length) {
        reviewList.innerHTML = '<li class="review-empty">No comments yet.</li>';
        return;
      }

      comments.forEach((comment) => {
        const item = document.createElement('li');
        item.className = 'review-item';
        item.innerHTML = `<strong>${comment.page}</strong> · ${comment.element} · ${comment.state}<br>${comment.comment}`;
        reviewList.appendChild(item);
      });
    }

    function setReviewMode(next) {
      reviewMode = next;
      document.body.classList.toggle('review-mode', reviewMode);
      reviewToggle.setAttribute('aria-pressed', String(reviewMode));
      reviewToggle.textContent = reviewMode ? 'Review Mode: ON' : 'Review Mode';
    }

    reviewToggle.addEventListener('click', function () {
      setReviewMode(!reviewMode);
    });

    reviewRoot.addEventListener('click', function (event) {
      if (!reviewMode) return;
      const target = event.target.closest('button, input, select, textarea, a, .card, .alert, .field, .row, h1, h2, h3, p, li, label, div');
      if (!target || target.closest('.toolbar') || target.closest('.review-panel')) return;

      const page = window.location.pathname.split('/').pop() || 'index.html';
      const elementName = selectorFor(target);
      const state = deriveState(target);
      const comment = window.prompt(`Comment for ${page} / ${elementName} / ${state}`);
      if (!comment) return;

      comments.push({
        id: `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`,
        page,
        element: elementName,
        selector: elementName,
        state,
        comment,
        reason: '',
        createdAt: new Date().toISOString(),
        annotation: {
          type: 'Annotation',
          motivation: 'commenting',
          target: {
            source: page,
            selector: { type: 'CssSelector', value: elementName }
          },
          body: [{ type: 'TextualBody', value: comment, purpose: 'commenting' }]
        }
      });
      saveComments(comments);
      renderList();
    });

    if (exportJsonButton) {
      exportJsonButton.addEventListener('click', function () {
        downloadFile('review-comments.json', JSON.stringify(comments, null, 2), 'application/json');
      });
    }

    if (exportMarkdownButton) {
      exportMarkdownButton.addEventListener('click', function () {
        downloadFile('review-comments.md', toMarkdown(comments), 'text/markdown');
      });
    }

    if (clearReviewButton) {
      clearReviewButton.addEventListener('click', function () {
        comments = [];
        saveComments(comments);
        renderList();
      });
    }

    renderList();
  });
})();
