(function () {
  function buildJson({ packId, version, annotations }) {
    return {
      meta: {
        tool: 'uidesign-review-mode-v2',
        pack_id: packId,
        exported_at: new Date().toISOString(),
        version
      },
      annotations
    };
  }

  function elementLabel(target) {
    if (target.data_review_id) return `[data-review-id="${target.data_review_id}"]`;
    if (target.css_selector) return target.css_selector;
    if (target.pin) return `Unlinked @${Math.round(target.pin.x)},${Math.round(target.pin.y)}`;
    return 'Unlinked';
  }

  function buildMarkdown(annotations) {
    const lines = [
      '# UIDesign Review Notes (generated)',
      '',
      '> Generated from Review Mode Export Markdown.',
      ''
    ];
    if (!annotations.length) {
      lines.push('- (No annotations)');
      return lines.join('\n');
    }
    annotations.forEach((item) => {
      lines.push(`- [${item.id}] Page: ${item.page}`);
      lines.push(`  - Element: ${elementLabel(item.target || {})}`);
      lines.push(`  - State: ${(item.ui_context && item.ui_context.state_hint) || 'default'}`);
      lines.push(`  - Status: ${item.status}`);
      lines.push(`  - Severity: ${item.severity}`);
      lines.push(`  - Change: ${(item.body && item.body.text) || ''}`);
      lines.push('  - Reason: (fill reason)');
    });
    return lines.join('\n');
  }

  function download(filename, content, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }

  async function copyMarkdown(markdown) {
    if (!navigator.clipboard || !window.isSecureContext) {
      throw new Error('Clipboard unavailable');
    }
    await navigator.clipboard.writeText(markdown);
  }

  async function importJsonFile(file) {
    const text = await file.text();
    const parsed = JSON.parse(text);
    return Array.isArray(parsed) ? parsed : parsed.annotations || [];
  }

  window.UIDesignReviewExport = {
    buildJson,
    buildMarkdown,
    download,
    copyMarkdown,
    importJsonFile
  };
})();
