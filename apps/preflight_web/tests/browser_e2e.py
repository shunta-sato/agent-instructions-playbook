"""Real browser -> HTTP -> SQLite walkthrough with a labelled deterministic provider.

Not a live Codex/model evaluation. Requires Playwright and Chromium.
Run from repository root: python apps/preflight_web/tests/browser_e2e.py
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import selectors
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[3]


def start(root: Path):
    process = subprocess.Popen([sys.executable, '-m', 'apps.preflight_web.server', '--port', '0',
                                '--state-dir', str(root), '--provider', 'demo'], cwd=ROOT,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    watch = selectors.DefaultSelector()
    watch.register(process.stdout, selectors.EVENT_READ)
    try:
        if not watch.select(8):
            raise RuntimeError('Local server did not start')
        url = process.stdout.readline().strip()
        if not url.startswith('http://127.0.0.1:'):
            raise RuntimeError('Local server readiness failed')
        return process, url
    except Exception:
        process.kill(); process.communicate()
        raise
    finally:
        watch.close()


def stop(process):
    process.terminate()
    try:
        process.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill(); process.communicate()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--screenshots', type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
        process, url = start(Path(tmp))
        browser = None
        try:
            browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium'), headless=True)
            context = browser.new_context(viewport={'width': 1440, 'height': 1000}, accept_downloads=True)
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(url)
            expect(page.get_by_role('heading', name='まず、同じ理解をつくる。')).to_be_visible()
            expect(page.locator('#provider')).to_contain_text('デモ')
            page.get_by_label('メッセージ').fill('設定を保存する機能を作りたい')
            page.get_by_role('button', name='送信', exact=True).click()
            expect(page.locator('#messages')).to_contain_text('すぐ選ばず')
            page.get_by_label('メッセージ').fill('なぜこの質問が必要？')
            page.get_by_role('button', name='送信', exact=True).click()
            expect(page.locator('#messages')).to_contain_text('聞き返しは選択や承認として扱いません')
            expect(page.locator('#agreement-status')).to_contain_text('未確定')
            page.get_by_label('メッセージ').fill('ローカルのみで。本番もCIも触らないで')
            page.get_by_role('button', name='送信', exact=True).click()
            expect(page.locator('#proposals')).to_contain_text('ローカル環境のみ')
            expect(page.locator('#field-environment')).to_have_value('')
            page.get_by_role('button', name='案に取り込む').click()
            expect(page.locator('#field-environment')).to_have_value('ローカル環境のみ。CI・本番は対象外。')
            expect(page.locator('#agreement-status')).to_contain_text('未確定')
            fields = {'outcome': '設定が再起動後も残る', 'non_goals': '本番デプロイしない',
                      'acceptance': '保存後に別プロセスで読み直し同じ値を確認',
                      'constraints': 'テストデータのみ。秘密情報なし', 'authority': '許可済みローカルの検証のみ'}
            for key, value in fields.items():
                page.locator('#field-' + key).fill(value)
            page.get_by_role('button', name='合意案を保存').click()
            expect(page.locator('#notice')).to_contain_text('保存しました')
            # Hold an old confirmation dialogue while another tab changes the agreement.
            page.get_by_role('button', name='内容を確認して確定').click()
            other = context.new_page(); other.goto(url)
            expect(other.locator('#field-authority')).to_have_value(fields['authority'])
            other.locator('#field-authority').fill('実行前に別途承認。現時点では対話のみ')
            other.get_by_role('button', name='合意案を保存').click()
            expect(other.locator('#notice')).to_contain_text('保存しました')
            page.get_by_label('これは内容の確認であり、実行許可ではないことを理解しました').check()
            page.get_by_role('button', name='この版を確定', exact=True).click()
            expect(page.locator('#notice')).to_contain_text('更新されました')
            page.get_by_role('button', name='相談に戻る').click()
            page.reload()
            expect(page.locator('#field-authority')).to_have_value('実行前に別途承認。現時点では対話のみ')
            expect(page.locator('#messages')).to_contain_text('なぜこの質問が必要？')
            page.get_by_role('button', name='内容を確認して確定').click()
            page.get_by_label('これは内容の確認であり、実行許可ではないことを理解しました').check()
            page.get_by_role('button', name='この版を確定', exact=True).click()
            expect(page.locator('#agreement-status')).to_contain_text('内容確認済み')
            expect(page.locator('#readiness')).to_contain_text('未検証')
            with page.expect_download() as download_info:
                page.get_by_role('button', name='引き継ぎJSON').click()
            handoff = json.loads(Path(download_info.value.path()).read_text())
            assert handoff['execution_authorized'] is False
            assert handoff['verification_status'] == 'not-run'
            assert handoff['agreement']['authority'].startswith('実行前に別途承認')
            if args.screenshots:
                args.screenshots.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(args.screenshots / 'preflight-console.png'), full_page=True)
            # Discussion never means authorization, even with HTML-looking input.
            page.get_by_label('メッセージ').fill('<img src=x onerror="window.hacked=true"> なぜ？')
            page.get_by_role('button', name='送信', exact=True).click()
            expect(page.locator('#agreement-status')).to_contain_text('未確定')
            expect(page.locator('#messages')).to_contain_text('<img src=x')
            assert page.locator('#messages img').count() == 0
            assert page.evaluate('window.hacked') is None
            expect(page.get_by_role('button', name='送信', exact=True)).to_be_enabled()
            assert not errors, errors
            # Full server restart, not merely SPA navigation.
            stop(process); process, new_url = start(Path(tmp))
            page.goto(new_url)
            expect(page.locator('#messages')).to_contain_text('なぜこの質問が必要？')
            expect(page.locator('#agreement-status')).to_contain_text('未確定')
            page.set_viewport_size({'width': 390, 'height': 844})
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
            print('PASS: real-browser dialogue, why, proposal vs draft, stale confirmation, explicit confirmation, export, XSS rendering, reload and server restart. Demo provider only.')
        finally:
            if browser is not None:
                browser.close()
            stop(process)


if __name__ == '__main__':
    main()
