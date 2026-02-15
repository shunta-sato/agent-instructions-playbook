(function () {
  const STORAGE_THEME = 'uidesign_theme';
  const STORAGE_VIEWPORT = 'uidesign_viewport';
  const STORAGE_ORIENTATION = 'uidesign_orientation';
  const STORAGE_SCALE_TO_FIT = 'uidesign_scale_to_fit';

  function getStorage(key, fallback) {
    try {
      const value = localStorage.getItem(key);
      return value === null ? fallback : value;
    } catch (_) {
      return fallback;
    }
  }

  function setStorage(key, value) {
    try {
      localStorage.setItem(key, value);
    } catch (_) {
      // Ignore storage errors for static previews.
    }
  }

  function setTheme(next) {
    if (next === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
    setStorage(STORAGE_THEME, next);
  }

  function getViewportPresetById(id) {
    const catalog = window.UIDESIGN_VIEWPORTS;
    if (!catalog || !catalog.presets) {
      return { id: 'fallback', label: 'Fallback (360×800)', width: 360, height: 800 };
    }
    return catalog.presets.find((preset) => preset.id === id) || catalog.presets[0];
  }

  function updateFrameSize(frame, preset, orientation) {
    const isLandscape = orientation === 'landscape';
    const width = isLandscape ? preset.height : preset.width;
    const height = isLandscape ? preset.width : preset.height;
    frame.style.setProperty('--viewport-width', `${width}px`);
    frame.style.setProperty('--viewport-height', `${height}px`);
  }

  function updateScaleToFit(stage, frame, enabled) {
    if (!enabled) {
      frame.style.setProperty('--viewport-scale', '1');
      return;
    }

    const frameWidth = frame.offsetWidth;
    const frameHeight = frame.offsetHeight;
    if (!frameWidth || !frameHeight) return;

    const padding = 24;
    const scaleX = (stage.clientWidth - padding) / frameWidth;
    const scaleY = (stage.clientHeight - padding) / frameHeight;
    const scale = Math.min(1, scaleX, scaleY);
    frame.style.setProperty('--viewport-scale', String(scale));
  }

  document.addEventListener('DOMContentLoaded', function () {
    const savedTheme = getStorage(STORAGE_THEME, 'light');
    setTheme(savedTheme === 'dark' ? 'dark' : 'light');

    const themeButton = document.getElementById('theme-toggle');
    if (themeButton) {
      themeButton.addEventListener('click', function () {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        setTheme(isDark ? 'light' : 'dark');
      });
    }

    const frame = document.querySelector('[data-device-frame]');
    const stage = document.querySelector('[data-device-stage]');
    const viewportSelect = document.getElementById('viewport-select');
    const orientationToggle = document.getElementById('orientation-toggle');
    const scaleToFitToggle = document.getElementById('scale-to-fit');
    if (!frame || !stage || !viewportSelect || !orientationToggle || !scaleToFitToggle) {
      return;
    }

    const presets = (window.UIDESIGN_VIEWPORTS && window.UIDESIGN_VIEWPORTS.presets) || [];
    presets.forEach((preset) => {
      const option = document.createElement('option');
      option.value = preset.id;
      option.textContent = preset.label;
      viewportSelect.appendChild(option);
    });

    const defaultViewportId = window.UIDESIGN_VIEWPORTS
      ? window.UIDESIGN_VIEWPORTS.getDefaultViewportId()
      : 'android-phone';

    let viewportId = getStorage(STORAGE_VIEWPORT, defaultViewportId);
    if (!presets.some((item) => item.id === viewportId)) viewportId = defaultViewportId;
    let orientation = getStorage(STORAGE_ORIENTATION, 'portrait');
    let scaleToFit = getStorage(STORAGE_SCALE_TO_FIT, 'true') === 'true';

    function renderFrame() {
      const preset = getViewportPresetById(viewportId);
      frame.dataset.viewportId = preset.id;
      frame.dataset.orientation = orientation;
      frame.querySelector('[data-viewport-label]').textContent =
        `${preset.label} / ${orientation === 'landscape' ? 'Landscape' : 'Portrait'}`;
      updateFrameSize(frame, preset, orientation);
      orientationToggle.textContent = orientation === 'portrait' ? 'Portrait' : 'Landscape';
      viewportSelect.value = preset.id;
      scaleToFitToggle.checked = scaleToFit;
      updateScaleToFit(stage, frame, scaleToFit);
    }

    viewportSelect.addEventListener('change', function () {
      viewportId = viewportSelect.value;
      setStorage(STORAGE_VIEWPORT, viewportId);
      renderFrame();
    });

    orientationToggle.addEventListener('click', function () {
      orientation = orientation === 'portrait' ? 'landscape' : 'portrait';
      setStorage(STORAGE_ORIENTATION, orientation);
      renderFrame();
    });

    scaleToFitToggle.addEventListener('change', function () {
      scaleToFit = scaleToFitToggle.checked;
      setStorage(STORAGE_SCALE_TO_FIT, String(scaleToFit));
      renderFrame();
    });

    window.addEventListener('resize', function () {
      updateScaleToFit(stage, frame, scaleToFit);
    });

    renderFrame();
  });
})();
