async function postJSON(url, payload) {
  const res = await fetch(url, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

document.getElementById('create-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const payload = Object.fromEntries(fd.entries());
  try {
    await postJSON('/api/instances', payload);
    location.reload();
  } catch (err) {
    alert('创建失败: ' + err.message);
  }
});

document.querySelectorAll('.launch-btn').forEach(btn => btn.addEventListener('click', async () => {
  try {
    await postJSON(`/api/instances/${btn.dataset.id}/launch`, {});
    location.reload();
  } catch (err) { alert(err.message); }
}));

async function distribute(id, type) {
  const file = prompt(`输入要分发的${type === 'experts' ? 'EA' : '指标'}文件完整路径`);
  if (!file) return;
  try {
    await postJSON('/api/distribute', { file_path: file, target_type: type, instance_ids: [Number(id)] });
    alert('分发成功');
  } catch (err) { alert(err.message); }
}

document.querySelectorAll('.dist-ea').forEach(btn => btn.addEventListener('click', () => distribute(btn.dataset.id, 'experts')));
document.querySelectorAll('.dist-ind').forEach(btn => btn.addEventListener('click', () => distribute(btn.dataset.id, 'indicators')));

document.querySelectorAll('.save-notes').forEach(btn => btn.addEventListener('click', async () => {
  const area = document.querySelector(`.notes[data-id="${btn.dataset.id}"]`);
  try {
    await fetch(`/api/instances/${btn.dataset.id}/notes`, {
      method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ notes: area.value })
    });
    alert('备注已同步');
  } catch (err) { alert(err.message); }
}));
