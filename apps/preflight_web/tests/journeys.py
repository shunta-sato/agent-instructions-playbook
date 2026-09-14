"""UI acceptance steps shared by real HTTP E2E and the separately labelled component test."""
from __future__ import annotations

from playwright.sync_api import expect


def chat(page, message):
    expect(page.locator('#send')).to_be_enabled()
    page.get_by_label('メッセージ').fill(message)
    page.get_by_role('button', name='送信', exact=True).click()
    expect(page.locator('#messages')).to_contain_text(message)
    expect(page.locator('#send')).to_be_enabled()


def confirm(page):
    page.get_by_role('button', name='内容を確認して確定').click()
    page.get_by_label('これは内容の確認であり、実行許可ではないことを理解しました').check()
    page.get_by_role('button', name='この版を確定', exact=True).click()
    expect(page.locator('#agreement-status')).to_contain_text('内容確認済み')


def exercise_console(page, other):
    expect(page.locator('#provider')).to_contain_text('デモ')
    chat(page, '設定を保存する機能を作りたい')
    expect(page.locator('#messages')).to_contain_text('すぐ選ばず')
    chat(page, 'なぜこの質問が必要？')
    expect(page.locator('#messages')).to_contain_text('聞き返しは選択や承認として扱いません')
    expect(page.locator('#agreement-status')).to_contain_text('未確定')
    chat(page, 'ローカルのみで。本番もCIも触らないで')
    expect(page.locator('#proposals')).to_contain_text('ローカル環境のみ')
    expect(page.locator('#field-environment')).to_have_value('')
    page.get_by_role('button', name='案に取り込む').click()
    expect(page.locator('#field-environment')).to_have_value('ローカル環境のみ。CI・本番は対象外。')
    values = {'outcome': '設定が再起動後も残る', 'non_goals': '本番デプロイしない',
              'acceptance': '保存後に別プロセスで読み直し同じ値を確認',
              'constraints': 'テストデータのみ。秘密情報なし', 'authority': '対話のみ'}
    for key, value in values.items():
        page.locator('#field-' + key).fill(value)
    page.get_by_role('button', name='合意案を保存').click()
    expect(page.locator('#notice')).to_contain_text('保存しました')
    expect(page.locator('#agreement-status')).to_contain_text('未確定')
    expect(other.locator('#field-outcome')).to_have_value(values['outcome'])

    # The old confirmation snapshot cannot authorize a newer draft.
    page.get_by_role('button', name='内容を確認して確定').click()
    other.locator('#field-authority').fill('実行前に別途承認。現時点では対話のみ')
    other.get_by_role('button', name='合意案を保存').click()
    expect(other.locator('#notice')).to_contain_text('保存しました')
    page.get_by_label('これは内容の確認であり、実行許可ではないことを理解しました').check()
    page.get_by_role('button', name='この版を確定', exact=True).click()
    expect(page.locator('#notice')).to_contain_text('更新されました')
    page.get_by_role('button', name='相談に戻る').click()
    expect(page.locator('#field-authority')).to_have_value('実行前に別途承認。現時点では対話のみ')

    # Local edits survive competing updates. Only explicitly reviewed fields overwrite.
    page.locator('#field-outcome').fill('このタブで編集した成果')
    other.locator('#field-outcome').fill('別のタブが保存した成果')
    other.locator('#field-constraints').fill('別のタブが追加した安全条件')
    other.get_by_role('button', name='合意案を保存').click()
    expect(page.locator('#conflict')).to_be_visible()
    expect(page.locator('#field-outcome')).to_have_value('このタブで編集した成果')
    page.get_by_role('button', name='最新との差分を確認').click()
    expect(page.locator('#merge-snapshot')).to_contain_text('別のタブが保存した成果')
    expect(page.locator('#merge-snapshot')).to_contain_text('このタブで編集した成果')
    # A competing write after opening the comparison must also be rejected.
    other.locator('#field-environment').fill('最新のローカル条件')
    other.get_by_role('button', name='合意案を保存').click()
    expect(other.locator('#notice')).to_contain_text('保存しました')
    page.get_by_role('button', name='表示した差分を保存').click()
    expect(page.locator('#notice')).to_contain_text('更新されました')
    page.get_by_role('button', name='編集に戻る').click()
    page.get_by_role('button', name='最新との差分を確認').click()
    page.get_by_role('button', name='表示した差分を保存').click()
    expect(page.locator('#merge-dialog')).not_to_be_visible()
    expect(page.locator('#field-outcome')).to_have_value('このタブで編集した成果')
    expect(page.locator('#field-constraints')).to_have_value('別のタブが追加した安全条件')
    expect(page.locator('#field-environment')).to_have_value('最新のローカル条件')
    expect(page.locator('#agreement-status')).to_contain_text('未確定')
    confirm(page)
    expect(page.locator('#readiness')).to_contain_text('未検証')


def exercise_safe_rendering(page):
    chat(page, '<img src=x onerror="window.hacked=true"> なぜ？')
    expect(page.locator('#agreement-status')).to_contain_text('未確定')
    expect(page.locator('#messages')).to_contain_text('<img src=x')
    expect(page.locator('#messages img')).to_have_count(0)
    if page.evaluate('window.hacked') is not None:
        raise AssertionError('Message HTML was executed')
