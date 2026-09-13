"""Dialogue boundary. Providers can propose text, never approve or execute work."""
from __future__ import annotations

from .state import FIELDS, text

REPLY_SCHEMA = {
    'type': 'object', 'additionalProperties': False,
    'properties': {
        'reply': {'type': 'string'},
        'proposals': {'type': 'array', 'items': {
            'type': 'object', 'additionalProperties': False,
            'properties': {'field': {'type': 'string', 'enum': list(FIELDS)},
                           'value': {'type': 'string'}, 'why': {'type': 'string'}},
            'required': ['field', 'value', 'why']}}},
    'required': ['reply', 'proposals']}

INSTRUCTIONS = '''You are the dialogue participant in Preflight Console. Respond in the user's
language. This is discussion, not a task-execution session. Explain why a question matters,
answer questions about your questions, and revise assumptions without demanding a numeric
choice. Use the supplied conversation and draft; do not pretend to have inspected code,
run tests or verified an environment. Ask only material unanswered questions, with a
bounded recommendation. Do not ask for secret values. A proposal, chat agreement, silence,
or urgency is not execution authorization. The server alone records human confirmation.
Return JSON matching the supplied schema: a natural-language reply and optional proposed
changes to the six agreement fields. Do not invent values merely to fill all fields.
For a why/explanation request with no new decision, proposals should normally be empty.
Never emit approval, readiness or tool commands as structured actions. Use no tools.
You cannot start implementation, access the project, or grant permissions from this UI.
'''


def validate_reply(value: object) -> dict:
    if not isinstance(value, dict) or set(value) != {'reply', 'proposals'}:
        raise ValueError('応答の形式が不正です。承認や実行指示は受理しません。')
    reply = text(value['reply'], 16000)
    if not reply.strip() or not isinstance(value['proposals'], list) or len(value['proposals']) > 6:
        raise ValueError('空の応答、または過剰な提案です。')
    seen, proposals = set(), []
    for proposal in value['proposals']:
        if not isinstance(proposal, dict) or set(proposal) != {'field', 'value', 'why'}:
            raise ValueError('不正な提案です。')
        field = proposal['field']
        if not isinstance(field, str) or field not in FIELDS or field in seen:
            raise ValueError('不明または重複した提案項目です。')
        seen.add(field)
        proposals.append({'field': field, 'value': text(proposal['value']), 'why': text(proposal['why'])})
    return {'reply': reply, 'proposals': proposals}


class DemoProvider:
    """Clearly labelled deterministic walkthrough, NOT a model or general assistant."""
    name = 'demo'
    label = 'デモ・定型応答（AI未接続）'

    def respond(self, state: dict) -> dict:
        message = state['messages'][-1]['text']
        if any(word in message.lower() for word in ('なぜ', '意図', 'why', '違い')):
            return {'reply': '【デモの定型説明】実装の最後に「環境がなくE2Eできなかった」とならないよう、'
                    'どの経路を実物で検証するかを先に確認する質問です。ローカルとCIの違いを相談したり、'
                    '認証だけ別環境にする案を検討できます。聞き返しは選択や承認として扱いません。', 'proposals': []}
        if 'ローカル' in message:
            return {'reply': '【デモの定型応答】ローカルのみという条件を提案欄に置きました。'
                    'まだ合意案も承認状態も変更していません。「案に取り込む」で確認・修正できます。'
                    '実際の起動確認は、この画面では行いません。',
                    'proposals': [{'field': 'environment', 'value': 'ローカル環境のみ。CI・本番は対象外。',
                                   'why': '直前の発言に「ローカル」が含まれています。意図と一致するか確認してください。'}]}
        return {'reply': '【デモの定型応答】この画面は自由に質問し返す流れを試すためのデモです。'
                '例として、E2Eの環境はローカルとCIのどちらを使うか考えます。'
                'すぐ選ばず「なぜこの質問が必要？」と聞いてみてください。'
                '実際の自由対話には、別途設定したCodex接続が必要です。', 'proposals': []}

    def close(self):
        pass
