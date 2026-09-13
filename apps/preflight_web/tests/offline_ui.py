"""Browser UI/component check with an in-process fixture transport; NOT HTTP E2E.

No localhost browser connection and no live model. The shipped HTML/CSS/JS are used;
only asset loading and fetch/sessionStorage are supplied by this offline test harness.
"""
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
                    store.finish_message(provider.respond(current))
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
            page = browser.new_page(viewport={'width': 1440, 'height': 1100}, accept_downloads=True)
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.expose_function('fixtureApi', transport)
            html = (static / 'index.html').read_text()
            html = re.sub(r'<link[^>]+>|<script[^>]+></script>', '', html)
            page.set_content(html)
            page.add_style_tag(content=(static / 'style.css').read_text())
            page.add_script_tag(content='''
                Object.defineProperty(window, 'sessionStorage', {value: {getItem: () => 'fixture'}});
                window.fetch = async (path, options = {}) => {
                    const result = await window.fixtureApi(path, options.body ? JSON.parse(options.body) : null);
                    return {ok: result.status < 400, status: result.status, json: async () => result.body};
                };
            ''')
            page.add_script_tag(content=(static / 'app.js').read_text())
            expect(page.locator('#provider')).to_contain_text('デモ')
            page.get_by_label('メッセージ').fill('設定保存を開発したい')
            page.get_by_role('button', name='送信', exact=True).click()
            expect(page.locator('#messages')).to_contain_text('すぐ選ばず')
            page.get_by_label('メッセージ').fill('なぜこの質問が必要？')
            page.get_by_role('button', name='送信', exact=True).click()
            expect(page.locator('#messages')).to_contain_text('聞き返しは選択や承認として扱いません')
            assert store.read()['approval'] is None
            page.get_by_label('メッセージ').fill('ローカルのみ。CI・本番は触らないで')
            page.get_by_role('button', name='送信', exact=True).click()
            expect(page.locator('#proposals')).to_contain_text('ローカル環境のみ')
            assert store.read()['draft']['environment'] == ''
            page.get_by_role('button', name='案に取り込む').click()
            values = {'outcome': '設定が再起動後も残る', 'non_goals': '本番デプロイはしない',
                'acceptance': '保存後に別プロセスで読み直し、同じ値を確認',
                'constraints': 'テストデータのみ。秘密情報は使用しない',
                'authority': '実行前に別途承認。現在は対話のみ'}
            for key, value in values.items(): page.locator('#field-' + key).fill(value)
            page.get_by_role('button', name='合意案を保存').click()
            expect(page.locator('#notice')).to_contain_text('保存しました')
            page.get_by_role('button', name='内容を確認して確定').click()
            # A competing write represents another browser session, not a mocked pass.
            store.edit(store.read()['revision'], {'authority': '本番・CIへのアクセスは禁止。現時点では対話のみ'})
            page.get_by_label('これは内容の確認であり、実行許可ではないことを理解しました').check()
            page.get_by_role('button', name='この版を確定', exact=True).click()
            expect(page.locator('#notice')).to_contain_text('更新されました')
            page.get_by_role('button', name='相談に戻る').click()
            expect(page.locator('#field-authority')).to_have_value('本番・CIへのアクセスは禁止。現時点では対話のみ')
            page.get_by_role('button', name='内容を確認して確定').click()
            page.get_by_label('これは内容の確認であり、実行許可ではないことを理解しました').check()
            page.get_by_role('button', name='この版を確定', exact=True).click()
            expect(page.locator('#agreement-status')).to_contain_text('内容確認済み')
            assert store.handoff()['execution_authorized'] is False
            if args.screenshot:
                args.screenshot.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(args.screenshot), full_page=True)
            # Unsaved edits must not absorb a newer revision and overwrite another writer.
            page.locator('#field-outcome').fill('古い画面の編集中')
            store.edit(store.read()['revision'], {'outcome': '他の画面で決めた新しい成果'})
            expect(page.locator('#agreement-status')).to_contain_text('未確定')
            page.get_by_role('button', name='合意案を保存').click()
            expect(page.locator('#notice')).to_contain_text('更新されました')
            assert store.read()['draft']['outcome'] == '他の画面で決めた新しい成果'
            page.set_viewport_size({'width': 390, 'height': 844})
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
            assert not errors, errors
            print('PASS: offline UI/component dialogue, why, proposals, stale confirm, human confirm, stale editor and responsive layout. Fixture transport; NOT browser HTTP E2E.')
        finally:
            browser.close(); store.close()


if __name__ == '__main__': main()
