'use strict';
const labels = {
  outcome: ['実現したい成果', 'OUTCOME'], non_goals: ['今回やらないこと', 'NON-GOALS'],
  acceptance: ['成功を確かめる経路・E2E', 'ACCEPTANCE'], constraints: ['品質・負荷・制約', 'CONSTRAINTS'],
  environment: ['検証環境と不足しているもの', 'ENVIRONMENT'], authority: ['許可範囲・確認が必要な操作', 'AUTHORITY']
};
const $ = id => document.getElementById(id);
let state = null, dirty = false, editRevision = null, confirmationRevision = null, stopped = false;
const storageKey = 'preflight-token-' + location.host;
const fragment = new URLSearchParams(location.hash.slice(1));
if (fragment.has('token')) {
  sessionStorage.setItem(storageKey, fragment.get('token'));
  history.replaceState(null, '', location.pathname);
}
const token = sessionStorage.getItem(storageKey) || '';

function element(tag, content, cls) {
  const node = document.createElement(tag);
  if (content !== undefined) node.textContent = content;
  if (cls) node.className = cls;
  return node;
}
function notice(message) { $('notice').textContent = message; }
async function api(path, payload) {
  const options = {headers: {Authorization: 'Bearer ' + token}, cache: 'no-store'};
  if (payload !== undefined) {
    options.method = 'POST'; options.headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(payload);
  }
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) {
    if (response.status === 401) stopped = true;
    throw new Error(data.error || '接続エラーです。再読み込みしてください。');
  }
  return data;
}
for (const [key, [label, en]] of Object.entries(labels)) {
  const field = element('div', undefined, 'field');
  const title = element('label', label); title.htmlFor = 'field-' + key;
  title.append(element('span', en));
  const input = element('textarea'); input.id = 'field-' + key; input.rows = 2; input.maxLength = 8000;
  input.placeholder = '対話で整理し、必要ならここで修正';
  input.addEventListener('input', () => { if (!dirty) editRevision = state.revision; dirty = true; updateButtons(); });
  field.append(title, input); $('fields').append(field);
}
function updateButtons() {
  const busy = !state || state.busy;
  $('send').disabled = busy;
  $('confirm').disabled = busy || dirty || !Object.values(state?.draft || {}).length ||
    !Object.values(state?.draft || {}).every(value => value.trim());
  $('export').disabled = busy || dirty || !state?.approval;
  $('draft-form').querySelector('button').disabled = busy || !dirty;
  $('dirty-note').textContent = dirty ? '未保存の変更があります' : '';
  $('thinking').hidden = !state?.busy;
}
function render(next) {
  if (state && next.revision === state.revision) { updateButtons(); return; }
  state = next;
  $('provider').textContent = state.provider_label;
  $('revision').textContent = '· v' + state.revision;
  $('agreement-status').textContent = state.approval ? '内容確認済み' : '未確定';
  $('agreement-status').classList.toggle('confirmed', !!state.approval);
  const messages = $('messages');
  const atBottom = messages.scrollHeight - messages.scrollTop - messages.clientHeight < 50;
  messages.replaceChildren();
  if (!state.messages.length) {
    const empty = element('div', undefined, 'empty');
    empty.append(element('strong', '「なぜ？」から始めても大丈夫。'),
      element('p', '質問の意味、推奨案の理由、前提の違い。その場で聞き返しながら、右側の合意案を一緒に整理します。'),
      element('p', '会話だけで合意の確定や実行許可にはなりません。'));
    messages.append(empty);
  }
  for (const item of state.messages) {
    const node = element('article', undefined, 'message ' + item.role);
    node.append(element('div', item.role === 'user' ? 'YOU' : (state.provider === 'demo' ? 'DEMO · NOT A MODEL' : 'CODEX'), 'role'),
      element('p', item.text));
    messages.append(node);
  }
  if (atBottom) messages.scrollTop = messages.scrollHeight;
  if (!dirty) for (const key of Object.keys(labels)) $('field-' + key).value = state.draft[key];
  $('proposals').replaceChildren();
  for (const proposal of state.proposals.filter(p => p.value !== state.draft[p.field])) {
    const box = element('div', undefined, 'proposal');
    box.append(element('strong', labels[proposal.field][0] + ' · AIの提案（未反映）'),
      element('pre', '現在: ' + (state.draft[proposal.field] || '未設定'), 'diff-before'),
      element('pre', '提案: ' + proposal.value, 'diff-after'), element('small', proposal.why));
    const apply = element('button', '案に取り込む'); apply.type = 'button'; apply.disabled = state.busy;
    apply.addEventListener('click', () => {
      $('field-' + proposal.field).value = proposal.value;
      if (!dirty) editRevision = state.revision;
      dirty = true; updateButtons();
      notice('編集欄へ取り込みました。内容を確認して「合意案を保存」してください。まだ確定していません。');
    });
    box.append(apply); $('proposals').append(box);
  }
  $('history').replaceChildren();
  for (const event of state.history.slice(-20).reverse()) {
    const names = {'message': '人間が発言', 'reply': 'AIが回答・提案', 'draft-edited': '人間が案を編集',
      'agreement-confirmed': '人間がこの版を確認', 'interrupted': '対話の中断・接続失敗'};
    $('history').append(element('p', 'v' + event.revision + ' · ' + (names[event.kind] || event.kind)));
    if (event.kind === 'draft-edited') {
      for (const [key, change] of Object.entries(event.detail)) {
        $('history').append(element('pre', labels[key][0] + '\n− ' + (change.before || '未設定') + '\n+ ' + change.after));
      }
    }
  }
  if (state.error) notice(state.error);
  updateButtons();
}
async function refresh() { render(await api('/api/state')); }
$('chat-form').addEventListener('submit', async event => {
  event.preventDefault();
  if (!state || state.busy) return;
  if (dirty) { notice('未保存の合意案があります。先に保存してください。'); return; }
  const message = $('message').value.trim();
  if (!message) return;
  $('send').disabled = true;
  try {
    const next = await api('/api/messages', {revision: state.revision, text: message});
    $('message').value = ''; notice('対話を続けます。確定済みだった内容も、再確認が必要になります。'); render(next);
  } catch (error) { notice(error.message); await refresh().catch(() => {}); }
});
$('message').addEventListener('keydown', event => {
  if (!event.isComposing && event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
    event.preventDefault(); if (!$('send').disabled) $('chat-form').requestSubmit();
  }
});
document.querySelectorAll('[data-prompt]').forEach(button => button.addEventListener('click', () => {
  $('message').value = button.dataset.prompt; $('message').focus();
}));
$('draft-form').addEventListener('submit', async event => {
  event.preventDefault();
  const fields = Object.fromEntries(Object.keys(labels).map(key => [key, $('field-' + key).value]));
  try {
    const next = await api('/api/draft', {revision: editRevision, fields});
    dirty = false; editRevision = null; render(next); notice('合意案を保存しました。内容はまだ確定していません。');
  } catch (error) { notice(error.message); }
});
$('confirm').addEventListener('click', () => {
  if (!state || state.busy || dirty) return;
  confirmationRevision = state.revision; $('reviewed').checked = false;
  $('confirm-snapshot').textContent = 'v' + state.revision + '\n\n' + Object.entries(state.draft)
    .map(([key, value]) => labels[key][0] + '\n' + value).join('\n\n');
  $('confirm-dialog').showModal();
});
$('back').addEventListener('click', () => { $('confirm-dialog').close(); confirmationRevision = null; });
$('approve').addEventListener('click', async () => {
  if (!$('reviewed').checked) { notice('確認欄にチェックを入れてください。'); return; }
  try {
    const next = await api('/api/approve', {revision: confirmationRevision, reviewed: true});
    render(next); $('confirm-dialog').close(); notice('この版の内容を確認済みとして記録しました。実行許可・E2E合格ではありません。');
  } catch (error) { notice(error.message); }
});
$('export').addEventListener('click', async () => {
  try {
    const data = await api('/api/handoff?revision=' + state.revision);
    const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2) + '\n'], {type: 'application/json'}));
    const link = element('a'); link.href = url; link.download = 'preflight-handoff.json'; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  } catch (error) { notice(error.message); }
});
async function poll() {
  if (stopped) return;
  try { if (!document.hidden) await refresh(); } catch (error) { notice(error.message); }
  if (!stopped) setTimeout(poll, 900);
}
if (!token) { stopped = true; notice('起動時に表示された #token= 付きURLを開いてください。'); updateButtons(); }
else poll();
