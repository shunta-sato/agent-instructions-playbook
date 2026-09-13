"""UI/component test with an in-process transport. NOT browser HTTP E2E or live AI."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from apps.preflight_web.providers import DemoProvider
from apps.preflight_web.state import SessionStore, Conflict
from apps.preflight_web.tests.journeys import exercise_console, exercise_safe_rendering
from playwright.sync_api import sync_playwright, expect


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--screenshot', type=Path)
    args = parser.parse_args()
    static = ROOT / 'apps/preflight_web/static'
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
        store, provider = SessionStore(Path(tmp) / 'ui.sqlite3'), DemoProvider()

        def snapshot():
            return dict(store.read(), provider=provider.name, provider_label=provider.label)

        def transport(path, data):
            try:
                route = urlsplit(path).path
                if route == '/api/messages':
                    current = store.begin_message(data['revision'], data['text'])
                    if data['text'] != '停止テスト':
                        store.finish_message(provider.respond(current), turn_id=current['active_turn'])
                elif route == '/api/cancel':
                    store.request_cancel(data['revision'], data['turn_id'])
                    store.fail_message('応答を停止しました。', turn_id=data['turn_id'])
                elif route == '/api/draft':
                    store.edit(data['revision'], data['fields'])
                elif route == '/api/approve':
                    store.approve(data['revision'], data['reviewed'])
                elif route == '/api/handoff':
                    rev = int(parse_qs(urlsplit(path).query)['revision'][0])
                    return {'status': 200, 'body': store.handoff(rev)}
                elif route != '/api/state':
                    raise ValueError('Unknown fixture request')
                return {'status': 200, 'body': snapshot()}
            except (Conflict, ValueError) as exc:
                return {'status': 409 if isinstance(exc, Conflict) else 400, 'body': {'error': str(exc)}}

        browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'), headless=True)
        try:
            context = browser.new_context(viewport={'width': 1440, 'height': 1100}, accept_downloads=True)
            errors = []

            def load(page):
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.expose_function('fixtureApi', transport)
                html = re.sub(r'<link[^>]+>|<script[^>]+></script>', '', (static / 'index.html').read_text())
                page.set_content(html)
                page.add_style_tag(content=(static / 'style.css').read_text())
                page.add_script_tag(content='''
                    const storage = new Map();
                    Object.defineProperty(window, 'sessionStorage', {value: {
                      getItem: key => key.startsWith('preflight-token-') ? 'fixture' : storage.get(key) || null,
                      setItem: (key, value) => storage.set(key, value),
                      removeItem: key => storage.delete(key)
                    }});
                    window.fetch = async (path, options = {}) => {
                      const result = await window.fixtureApi(path, options.body ? JSON.parse(options.body) : null);
                      return {ok: result.status < 400, status: result.status, json: async () => result.body};
                    };
                ''')
                page.add_script_tag(content=(static / 'app.js').read_text())

            page, other = context.new_page(), context.new_page()
            load(page)
            load(other)
            exercise_console(page, other)
            if store.handoff()['execution_authorized'] is not False:
                raise AssertionError('Content confirmation became execution authority')
            if args.screenshot:
                args.screenshot.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(args.screenshot), full_page=True)
            exercise_safe_rendering(page)
            page.locator('#message').fill('停止テスト')
            page.locator('#send').click()
            expect(page.locator('#cancel-response')).to_be_visible()
            page.locator('#cancel-response').click()
            expect(page.locator('#cancel-response')).not_to_be_visible()
            expect(page.locator('#messages')).to_contain_text('応答中断')
            expect(page.locator('#send')).to_be_enabled()
            page.set_viewport_size({'width': 390, 'height': 844})
            if not page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'):
                raise AssertionError('Mobile viewport overflows')
            if errors:
                raise AssertionError(errors)
            print('PASS: offline UI/component — dialogue, why, proposals, stale confirmation, conflict review, cancellation and responsive layout. Fixture transport; NOT browser HTTP E2E.')
        finally:
            browser.close()
            store.close()


if __name__ == '__main__':
    main()
