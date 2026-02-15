(function () {
  const STORAGE_KEY = 'uidesign_viewport_state';
  const PRESETS = [
    { id: 'android-phone', label: 'Android Phone (360×800)', width: 360, height: 800 },
    { id: 'android-large', label: 'Android Large (412×915)', width: 412, height: 915 },
    { id: 'android-tablet', label: 'Android Tablet (800×1280)', width: 800, height: 1280 },
    { id: 'web-desktop', label: 'Web Desktop (1280×800)', width: 1280, height: 800 }
  ];

  function loadState() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
    } catch (_) {
      return {};
    }
  }

  function saveState(state) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch (_) {}
  }

  function getDefaultPresetId(platforms) {
    if (Array.isArray(platforms) && platforms.includes('android')) {
      return 'android-phone';
    }
    return 'web-desktop';
  }

  function init(options) {
    const platforms = (options && options.platforms) || [];
    const stage = document.getElementById('previewStage');
    const frame = document.getElementById('deviceFrame');
    const canvas = document.getElementById('deviceCanvas');
    const select = document.getElementById('viewportSelect');
    const orientationToggle = document.getElementById('orientationToggle');
    const scaleToFitToggle = document.getElementById('scaleToFitToggle');
    const sizeLabel = document.getElementById('viewportSizeLabel');

    if (!stage || !frame || !canvas || !select) return;

    const savedState = loadState();
    const defaultPresetId = getDefaultPresetId(platforms);
    const state = {
      presetId: savedState.presetId || defaultPresetId,
      orientation: savedState.orientation || 'portrait',
      scaleToFit: savedState.scaleToFit !== false
    };

    PRESETS.forEach((preset) => {
      const option = document.createElement('option');
      option.value = preset.id;
      option.textContent = preset.label;
      select.appendChild(option);
    });

    function applyViewport() {
      const preset = PRESETS.find((item) => item.id === state.presetId) || PRESETS[0];
      const isLandscape = state.orientation === 'landscape';
      const width = isLandscape ? preset.height : preset.width;
      const height = isLandscape ? preset.width : preset.height;

      frame.style.width = `${width}px`;
      frame.style.height = `${height}px`;
      sizeLabel.textContent = `${width} × ${height}`;

      if (state.scaleToFit) {
        const stageRect = stage.getBoundingClientRect();
        const scaleX = Math.max(0.2, (stageRect.width - 24) / width);
        const scaleY = Math.max(0.2, (stageRect.height - 24) / height);
        canvas.style.setProperty('--viewport-scale', String(Math.min(1, scaleX, scaleY)));
      } else {
        canvas.style.setProperty('--viewport-scale', '1');
      }

      select.value = preset.id;
      orientationToggle.textContent = isLandscape ? 'Portrait' : 'Landscape';
      scaleToFitToggle.textContent = state.scaleToFit ? 'Scale: Fit' : 'Scale: 100%';

      saveState(state);
    }

    select.addEventListener('change', (event) => {
      state.presetId = event.target.value;
      applyViewport();
    });

    orientationToggle.addEventListener('click', () => {
      state.orientation = state.orientation === 'portrait' ? 'landscape' : 'portrait';
      applyViewport();
    });

    scaleToFitToggle.addEventListener('click', () => {
      state.scaleToFit = !state.scaleToFit;
      applyViewport();
    });

    window.addEventListener('resize', applyViewport);
    applyViewport();
  }

  window.UIDesignViewport = { init };
})();
