(function () {
  const VIEWPORT_PRESETS = [
    { id: 'android-phone', label: 'Android Phone (360×800)', width: 360, height: 800 },
    { id: 'android-large', label: 'Android Large (412×915)', width: 412, height: 915 },
    { id: 'android-tablet', label: 'Android Tablet (800×1280)', width: 800, height: 1280 },
    { id: 'tablet', label: 'Tablet (768×1024)', width: 768, height: 1024 },
    { id: 'desktop', label: 'Desktop (1280×800)', width: 1280, height: 800 }
  ];

  function normalizePlatforms(platforms) {
    if (!platforms) return [];
    if (Array.isArray(platforms)) return platforms.map((item) => String(item).toLowerCase());
    return String(platforms)
      .split(',')
      .map((item) => item.trim().toLowerCase())
      .filter(Boolean);
  }

  function resolvePlatforms() {
    if (window.UIUX_META && window.UIUX_META.meta && window.UIUX_META.meta.platforms) {
      return normalizePlatforms(window.UIUX_META.meta.platforms);
    }

    const fromMeta = document.querySelector('meta[name="uiux-platforms"]');
    if (fromMeta && fromMeta.content) {
      return normalizePlatforms(fromMeta.content);
    }

    return [];
  }

  function getDefaultViewportId() {
    const platforms = resolvePlatforms();
    return platforms.includes('android') ? 'android-phone' : 'desktop';
  }

  window.UIDESIGN_VIEWPORTS = {
    presets: VIEWPORT_PRESETS,
    getDefaultViewportId
  };
})();
