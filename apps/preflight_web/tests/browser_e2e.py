"""Real browser -> HTTP -> SQLite; demo and cancellation fixture only, not live AI.

Run only in an approved browser verification environment. Navigation denial is a
failure, not permission to modify policies, switch hosts or substitute fixture transport.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import tempfile

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from apps.preflight_web.tests.journeys import chat, exercise_console, exercise_safe_rendering


def start(root: Path, *, module='apps.preflight_web.server', port=0):
    argv = [sys.executable, '-m', module, '--port', str(port), '--state-dir', str(root)]
    if module == 'apps.preflight_web.server':
        argv += ['--provider', 'demo']
    process = subprocess.Popen(argv, cwd=ROOT,
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
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
        stop(process)
        raise
    finally:
        watch.close()


def stop(process):
    if process.poll() is None:
        process.send_signal(signal.SIGINT)
    try:
        process.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()


def navigate(page, url):
    try:
        page.goto(url)
        expect(page.locator('#provider')).to_contain_text('デモ')
    except Exception as exc:
        # Do not put the ephemeral session token into CI logs.
        message = str(exc).replace(url, '[local test URL]')
        raise RuntimeError(message) from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--screenshots', type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
        process, url = start(Path(tmp))
        browser = None
        try:
            options = {'headless': True}
            if os.environ.get('CHROMIUM_PATH'):
                options['executable_path'] = os.environ['CHROMIUM_PATH']
            browser = p.chromium.launch(**options)
            print('Browser:', browser.version)
            context = browser.new_context(viewport={'width': 1440, 'height': 1100}, accept_downloads=True)
            page, other = context.new_page(), context.new_page()
            errors = []
            for tab in (page, other):
                tab.on('pageerror', lambda error: errors.append(str(error)))
                tab.on('dialog', lambda dialog: dialog.accept())
                navigate(tab, url)
            exercise_console(page, other)
            with page.expect_download() as info:
                page.get_by_role('button', name='引き継ぎJSON').click()
            handoff = json.loads(Path(info.value.path()).read_text())
            if handoff['execution_authorized'] is not False or handoff['verification_status'] != 'not-run':
                raise AssertionError('Handoff granted authority or claimed verification')
            if handoff['agreement']['constraints'] != '別のタブが追加した安全条件':
                raise AssertionError('Unedited remote field was overwritten')
            if args.screenshots:
                args.screenshots.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(args.screenshots / 'preflight-console.png'), full_page=True)
            exercise_safe_rendering(page)
            page.locator('#field-outcome').fill('再読み込みしても残す未保存の案')
            page.locator('#message').fill('まだ送信しない質問')
            page.reload()
            expect(page.locator('#field-outcome')).to_have_value('再読み込みしても残す未保存の案')
            expect(page.locator('#message')).to_have_value('まだ送信しない質問')
            expect(page.locator('#dirty-note')).to_contain_text('未保存')
            page.get_by_role('button', name='合意案を保存').click()
            expect(page.locator('#notice')).to_contain_text('保存しました')

            # Keep the origin fixed so the restart test also verifies native sessionStorage.
            port = int(page.url.split(':')[2].split('/')[0])
            stop(process)
            process, new_url = start(Path(tmp), port=port)
            navigate(page, new_url)
            expect(page.locator('#messages')).to_contain_text('なぜこの質問が必要？')
            expect(page.locator('#message')).to_have_value('まだ送信しない質問')
            expect(page.locator('#field-outcome')).to_have_value('再読み込みしても残す未保存の案')
            expect(page.locator('#agreement-status')).to_contain_text('未確定')
            # Reload does not post the saved, unsent message.
            expect(page.locator('#messages')).not_to_contain_text('まだ送信しない質問')
            page.set_viewport_size({'width': 390, 'height': 844})
            if not page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'):
                raise AssertionError('Mobile viewport overflows')

            stop(process)
            process, new_url = start(Path(tmp), module='apps.preflight_web.tests.slow_demo_server')
            navigate(page, new_url)
            page.locator('#message').fill('停止テスト')
            page.locator('#send').click()
            expect(page.locator('#cancel-response')).to_be_visible()
            page.locator('#cancel-response').click()
            expect(page.locator('#cancel-response')).not_to_be_visible()
            expect(page.locator('#messages')).to_contain_text('応答中断')
            chat(page, 'なぜこの質問が必要？')
            expect(page.locator('#messages .assistant').last).to_contain_text('聞き返しは選択や承認')
            expect(page.locator('#agreement-status')).to_contain_text('未確定')
            if errors:
                raise AssertionError(errors)
            print('PASS: real browser/HTTP/SQLite dialogue, conflict recovery, stale confirmation, handoff, text rendering, native storage, restart and cancellation. Demo/fixture providers only; not live AI.')
        finally:
            if browser is not None:
                browser.close()
            stop(process)


if __name__ == '__main__':
    main()
