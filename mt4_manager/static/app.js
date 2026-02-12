async function requestJSON(url, method = 'GET', payload = null) {
  const init = { method, headers: {} };
  if (payload !== null) {
    init.headers['Content-Type'] = 'application/json';
    init.body = JSON.stringify(payload);
  }
  const res = await fetch(url, init);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function askFile(label) {
  const value = prompt(`输入要分发的${label}文件完整路径`);
  if (!value) return null;
  return value;
}

document.getElementById('create-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = Object.fromEntries(new FormData(e.target).entries());
  try {
    await requestJSON('/api/instances', 'POST', payload);
    location.reload();
  } catch (err) {
    alert('创建失败: ' + err.message);
  }
});

document.querySelectorAll('.launch-btn').forEach((btn) => btn.addEventListener('click', async () => {
  try {
    await requestJSON(`/api/instances/${btn.dataset.id}/launch`, 'POST', {});
    location.reload();
  } catch (err) {
    alert(err.message);
  }
}));

async function distributeByInstance(instanceId, type) {
  const file = askFile(type === 'experts' ? 'EA' : '指标');
  if (!file) return;
  try {
    await requestJSON('/api/distribute', 'POST', { file_path: file, target_type: type, instance_ids: [Number(instanceId)] });
    alert('分发成功');
  } catch (err) {
    alert(err.message);
  }
}

document.querySelectorAll('.dist-ea').forEach((btn) => btn.addEventListener('click', () => distributeByInstance(btn.dataset.id, 'experts')));
document.querySelectorAll('.dist-ind').forEach((btn) => btn.addEventListener('click', () => distributeByInstance(btn.dataset.id, 'indicators')));

document.querySelectorAll('.save-notes').forEach((btn) => btn.addEventListener('click', async () => {
  const area = document.querySelector(`.notes[data-id="${btn.dataset.id}"]`);
  try {
    await requestJSON(`/api/instances/${btn.dataset.id}/notes`, 'PATCH', { notes: area.value });
    alert('备注已同步');
  } catch (err) {
    alert(err.message);
  }
}));

async function distributeByGroup(type) {
  const group = document.getElementById('group-select')?.value || null;
  const file = askFile(type === 'experts' ? 'EA' : '指标');
  if (!file) return;

  const payload = { file_path: file, target_type: type, all_instances: !group };
  if (group) payload.group_name = group;

  try {
    const res = await requestJSON('/api/distribute', 'POST', payload);
    alert(`批量分发完成: ${res.results.length} 个实例`);
  } catch (err) {
    alert(err.message);
  }
}

document.getElementById('dist-group-ea-btn')?.addEventListener('click', () => distributeByGroup('experts'));
document.getElementById('dist-group-ind-btn')?.addEventListener('click', () => distributeByGroup('indicators'));

document.getElementById('launch-all-btn')?.addEventListener('click', async () => {
  try {
    const res = await requestJSON('/api/launch', 'POST');
    alert(`启动完成: ${res.results.length} 个实例`);
    location.reload();
  } catch (err) {
    alert(err.message);
  }
});

document.getElementById('launch-group-btn')?.addEventListener('click', async () => {
  const group = document.getElementById('group-select')?.value || '';
  const query = group ? `?group_name=${encodeURIComponent(group)}` : '';
  try {
    const res = await requestJSON(`/api/launch${query}`, 'POST');
    alert(`按组启动完成: ${res.results.length} 个实例`);
    location.reload();
  } catch (err) {
    alert(err.message);
  }
});
