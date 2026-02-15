(function () {
  function setTheme(next) {
    if (next === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
    try { localStorage.setItem('uidesign_theme', next); } catch (_) {}
  }

  function getTheme() {
    try { return localStorage.getItem('uidesign_theme'); } catch (_) { return null; }
  }

  function detectPlatforms() {
    const attr = document.documentElement.getAttribute('data-uiux-platforms') || '';
    const normalized = attr.trim().toLowerCase();

    if (!normalized || normalized.includes('<fill')) {
      return ['android'];
    }

    const values = normalized
      .split(',')
      .map((value) => value.trim())
      .filter(Boolean);
    return values;
  }

  document.addEventListener('DOMContentLoaded', function () {
    const saved = getTheme();
    if (saved === 'dark') setTheme('dark');

    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) {
      themeBtn.addEventListener('click', function () {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        setTheme(isDark ? 'light' : 'dark');
      });
    }

    if (window.UIDesignViewport) {
      window.UIDesignViewport.init({
        platforms: detectPlatforms()
      });
    }

    if (window.UIDesignReview) {
      window.UIDesignReview.init();
    }
  });
})();
