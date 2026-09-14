'use strict';
const labels = {
  outcome: ['実現したい成果', 'OUTCOME'], non_goals: ['今回やらないこと', 'NON-GOALS'],
  acceptance: ['成功を確かめる経路・E2E', 'ACCEPTANCE'], constraints: ['品質・負荷・制約', 'CONSTRAINTS'],
  environment: ['検証環境と不足しているもの', 'ENVIRONMENT'], authority: ['許可範囲・確認が必要な操作', 'AUTHORITY']
};
const $ = id => document.getElementById(id);
let state = null, editor = null, confirmationRevision = null, stopped = false;
let posting = false, connected = false, recoveryKey = null, composerKey = null;
let mergeRevision = null, mergeFields = null;
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
function saveRecovery() {
  if (!recoveryKey) return;
  try {
    if (editor) sessionStorage.setItem(recoveryKey, JSON.stringify(editor));
    else sessionStorage.removeItem(recoveryKey);
  } catch (_) {
    notice('このタブに編集内容を保存できません。再読み込み前に入力を控えてください。');
  }
}
function saveComposer() {
  if (!composerKey) return;
  try { sessionStorage.setItem(composerKey, $('message').value); }
  catch (_) { notice('未送信の入力を保存できません。再読み込み前に入力を控えてください。'); }
}
function changeField(key, value) {
  if (!state || posting) return;
  if (!editor) editor = {revision: state.revision, base: {...state.draft}, fields: {...state.draft}};
  editor.fields[key] = value;
  if (Object.keys(labels).every(name => editor.fields[name] === editor.base[name])) editor = null;
  saveRecovery();
  updateButtons();
}
function editedFields() {
  return Object.fromEntries(Object.keys(labels).filter(key => editor.fields[key] !== editor.base[key])
    .map(key => [key, editor.fields[key]]));
}
async function api(path, payload) {
  const options = {headers: {Authorization: 'Bearer ' + token}, cache: 'no-store',
    signal: AbortSignal.timeout(10000)};
  if (payload !== undefined) {
    options.method = 'POST';
    options.headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(payload);
  }
  let response;
  try { response = await fetch(path, options); }
  catch (_) {
    connected = false;
    updateButtons();
    throw new Error('接続が切れたか応答待ちが期限切れです。入力は保持し、自動再送しません。再接続後に状態を確認してください。');
  }
  const data = await response.json();
  if (!response.ok) {
    if (response.status === 401) { stopped = true; connected = false; }
    const error = new Error(data.error || '接続エラーです。');
    error.status = response.status;
    updateButtons();
    throw error;
  }
  connected = true;
  return data;
}
for (const [key, [label, en]] of Object.entries(labels)) {
  const field = element('div', undefined, 'field');
  const title = element('label', label);
  title.htmlFor = 'field-' + key;
  title.append(element('span', en));
  const input = element('textarea');
  input.id = 'field-' + key;
  input.rows = 2;
  input.maxLength = 8000;
  input.placeholder = '対話で整理し、必要ならここで修正';
  input.addEventListener('input', () => changeField(key, input.value));
  field.append(title, input);
  $('fields').append(field);
}
function updateButtons() {
  const unavailable = !connected || stopped || posting || !state;
  const busy = unavailable || state.busy;
  $('send').disabled = busy || !!editor;
  $('message').disabled = posting;
  $('cancel-response').hidden = !state?.busy;
  $('cancel-response').disabled = unavailable || !state?.busy || state?.cancel_requested;
  $('cancel-response').textContent = state?.cancel_requested ? '停止を確認中…' : '応答を止めて相談に戻る';
  $('confirm').disabled = busy || !!editor || !Object.values(state?.draft || {}).length ||
    !Object.values(state?.draft || {}).every(value => value.trim());
  $('export').disabled = busy || !!editor || !state?.approval;
  $('draft-form').querySelector('button').disabled = busy || !editor;
  for (const key of Object.keys(labels)) $('field-' + key).disabled = !state || posting;
  $('dirty-note').textContent = editor ? '未保存の変更をこのタブに保持しています' : '';
  $('conflict').hidden = !editor || !state || editor.revision === state.revision;
  $('resolve').disabled = busy;
  $('discard').disabled = busy;
  $('thinking').hidden = !state?.busy;
  $('thinking').textContent = state?.cancel_requested ?
    '停止を確認しています。次の送信は停止完了後です。' : '応答を待っています。内容確認・実行許可にはなりません。';
  $('connection').textContent = stopped ? '要再ログイン：起動URLを開いてください' :
    (connected ? '接続中' : '未接続・入力は保持');
  document.querySelectorAll('.proposal button').forEach(button => { button.disabled = busy; });
}
function restoreEditor(next) {
  const key = 'preflight-editor-' + next.session_id;
  if (key === recoveryKey) return;
  recoveryKey = key;
  composerKey = 'preflight-message-' + next.session_id;
  editor = null;
  try {
    const message = sessionStorage.getItem(composerKey) || '';
    if (message.length <= 8000) $('message').value = message;
    const saved = JSON.parse(sessionStorage.getItem(key) || 'null');
    if (saved && Number.isInteger(saved.revision) && saved.revision <= next.revision &&
        Object.keys(labels).every(name => typeof saved.base?.[name] === 'string' &&
          typeof saved.fields?.[name] === 'string' && saved.fields[name].length <= 8000)) {
      editor = saved;
      notice('このタブの未保存の編集を復元しました。最新の保存内容と比較してから保存できます。');
    }
  } catch (_) { notice('編集内容を復元できません。保存済みの内容を表示します。'); }
}
function render(next) {
  if (state && next.session_id === state.session_id && next.revision <= state.revision) {
    if (!editor) for (const key of Object.keys(labels)) $('field-' + key).value = state.draft[key];
    updateButtons();
    return; // Late polling responses must not roll the UI back.
  }
  restoreEditor(next);
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
    const speaker = item.role === 'user' ? 'YOU' : (state.provider === 'demo' ? 'DEMO · NOT A MODEL' : 'CODEX');
    node.append(element('div', speaker + (item.status === 'interrupted' ? ' · 応答中断' : ''), 'role'),
      element('p', item.text));
    messages.append(node);
  }
  if (atBottom) messages.scrollTop = messages.scrollHeight;
  for (const key of Object.keys(labels)) $('field-' + key).value = editor ? editor.fields[key] : state.draft[key];
  $('proposals').replaceChildren();
  for (const proposal of state.proposals.filter(p => p.value !== state.draft[p.field])) {
    const box = element('div', undefined, 'proposal');
    box.append(element('strong', labels[proposal.field][0] + ' · AIの提案（未反映）'),
      element('pre', '現在: ' + (state.draft[proposal.field] || '未設定'), 'diff-before'),
      element('pre', '提案: ' + proposal.value, 'diff-after'), element('small', proposal.why));
    const apply = element('button', '案に取り込む');
    apply.type = 'button';
    apply.addEventListener('click', () => {
      $('field-' + proposal.field).value = proposal.value;
      changeField(proposal.field, proposal.value);
      notice('編集欄へ取り込みました。「合意案を保存」の前に内容を確認してください。まだ確定していません。');
    });
    box.append(apply);
    $('proposals').append(box);
  }
  $('history').replaceChildren();
  for (const event of state.history.slice(-20).reverse()) {
    const names = {'message': '人間が発言', 'reply': 'AIが回答・提案', 'draft-edited': '人間が案を編集',
      'agreement-confirmed': '人間がこの版を確認', 'interrupted': '対話の中断・接続失敗',
      'cancel-requested': '人間が応答の停止を要求'};
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
async function mutate(path, payload, onSuccess) {
  if (posting || !connected || stopped) return;
  posting = true;
  updateButtons();
  try {
    const next = await api(path, payload);
    onSuccess(next);
    render(next);
  } catch (error) {
    notice(error.message);
    await refresh().catch(() => {});
  } finally { posting = false; updateButtons(); }
}
$('chat-form').addEventListener('submit', event => {
  event.preventDefault();
  if (!state || state.busy || editor) return;
  const message = $('message').value.trim();
  if (!message) return;
  mutate('/api/messages', {revision: state.revision, text: message}, () => {
    $('message').value = '';
    saveComposer();
    notice('対話を続けます。確定済みだった内容も再確認が必要です。');
  });
});
$('cancel-response').addEventListener('click', () => {
  if (!state?.busy || state.cancel_requested) return;
  mutate('/api/cancel', {revision: state.revision, turn_id: state.active_turn}, () => {
    notice('応答の停止を要求しました。停止の確認後に質問を直して送信できます。自動再送はしません。');
  });
});
$('message').addEventListener('input', saveComposer);
$('message').addEventListener('keydown', event => {
  if (!event.isComposing && event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
    event.preventDefault();
    if (!$('send').disabled) $('chat-form').requestSubmit();
  }
});
document.querySelectorAll('[data-prompt]').forEach(button => button.addEventListener('click', () => {
  $('message').value = button.dataset.prompt;
  saveComposer();
  $('message').focus();
}));
function savedDraft() {
  editor = null;
  saveRecovery();
  notice('合意案を保存しました。内容はまだ確定していません。');
}
function showMerge() {
  if (!editor || !state || state.busy) return;
  mergeRevision = state.revision;
  mergeFields = editedFields();
  $('merge-snapshot').textContent = '最新 v' + mergeRevision + ' に重ねる変更\n\n' +
    Object.entries(mergeFields).map(([key, value]) => labels[key][0] + '\n編集開始時: ' +
      editor.base[key] + '\n現在の保存値: ' + state.draft[key] + '\nあなたの変更: ' + value).join('\n\n');
  $('merge-dialog').showModal();
}
$('draft-form').addEventListener('submit', event => {
  event.preventDefault();
  if (!editor || !state || state.busy) return;
  if (editor.revision !== state.revision) { showMerge(); return; }
  mutate('/api/draft', {revision: editor.revision, fields: editedFields()}, savedDraft);
});
$('resolve').addEventListener('click', showMerge);
$('merge-back').addEventListener('click', () => $('merge-dialog').close());
$('merge-save').addEventListener('click', () => {
  if (!editor) return;
  mutate('/api/draft', {revision: mergeRevision, fields: mergeFields}, () => {
    savedDraft();
    $('merge-dialog').close();
  });
});
$('discard').addEventListener('click', () => {
  if (!window.confirm('このタブの未保存の編集を破棄し、最新の保存内容を表示しますか？')) return;
  editor = null;
  saveRecovery();
  for (const key of Object.keys(labels)) $('field-' + key).value = state.draft[key];
  updateButtons();
});
$('confirm').addEventListener('click', () => {
  if (!state || state.busy || editor) return;
  confirmationRevision = state.revision;
  $('reviewed').checked = false;
  $('confirm-snapshot').textContent = 'v' + state.revision + '\n\n' + Object.entries(state.draft)
    .map(([key, value]) => labels[key][0] + '\n' + value).join('\n\n');
  $('confirm-dialog').showModal();
});
$('back').addEventListener('click', () => { $('confirm-dialog').close(); confirmationRevision = null; });
$('approve').addEventListener('click', () => {
  if (!$('reviewed').checked) { notice('確認欄にチェックを入れてください。'); return; }
  mutate('/api/approve', {revision: confirmationRevision, reviewed: true}, () => {
    $('confirm-dialog').close();
    notice('この版の内容を確認済みとして記録しました。実行許可・E2E合格ではありません。');
  });
});
$('export').addEventListener('click', async () => {
  try {
    const data = await api('/api/handoff?revision=' + state.revision);
    const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2) + '\n'], {type: 'application/json'}));
    const link = element('a');
    link.href = url;
    link.download = 'preflight-handoff.json';
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  } catch (error) { notice(error.message); }
});
async function poll() {
  if (stopped) return;
  try { if (!document.hidden) await refresh(); } catch (error) { notice(error.message); }
  if (!stopped) setTimeout(poll, 900);
}
window.addEventListener('beforeunload', event => {
  if (editor) { event.preventDefault(); event.returnValue = ''; }
});
if (!token) { stopped = true; notice('起動時に表示された #token= 付きURLを開いてください。'); updateButtons(); }
else poll();
