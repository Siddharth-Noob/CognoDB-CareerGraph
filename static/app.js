const rolesEl = document.querySelector('#roles');
const resultsEl = document.querySelector('#results');
const healthEl = document.querySelector('#health');

async function getJSON(url) {
  const response = await fetch(url);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || data.message || 'Request failed');
  return data;
}

function pills(items) {
  return (items || []).map(x => `<span class="pill">${escapeHtml(x)}</span>`).join('');
}
function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>\"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
}

async function loadHealth() {
  try {
    await getJSON('/api/health');
    healthEl.textContent = '● CognoDB connected';
  } catch (e) {
    healthEl.textContent = '● Database unavailable';
    healthEl.style.color = '#ff9ca8';
  }
}

async function loadRoles() {
  rolesEl.innerHTML = '<div class="spinner">Loading roles…</div>';
  try {
    const roles = await getJSON('/api/roles');
    if (!roles.length) { rolesEl.innerHTML = '<div class="empty">No roles found. Run the seed script.</div>'; return; }
    rolesEl.innerHTML = roles.map(r => `
      <article class="role">
        <h3>${escapeHtml(r.title)}</h3>
        <span class="pill">${escapeHtml(r.level)}</span>
        <p class="company">Graph node · Role ${escapeHtml(r.id)}</p>
        <div>${pills(r.skills)}</div>
      </article>`).join('');
  } catch (e) {
    rolesEl.innerHTML = `<div class="card error">${escapeHtml(e.message)}</div>`;
  }
}

document.querySelector('#search-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const skill = document.querySelector('#skill').value.trim();
  if (!skill) return;
  resultsEl.innerHTML = '<div class="card spinner">Traversing the graph…</div>';
  try {
    const data = await getJSON(`/api/recommendations?skill=${encodeURIComponent(skill)}`);
    if (!data.length) {
      resultsEl.innerHTML = `<div class="card empty">No connections found for <strong>${escapeHtml(skill)}</strong>. Try another skill.</div>`;
      return;
    }
    resultsEl.innerHTML = `<div class="card"><p class="eyebrow">MULTI-HOP RESULTS</p><h2 class="result-title">Connections for “${escapeHtml(skill)}”</h2><div class="result-grid">${data.map(r => `
      <article class="result-item"><h3>${escapeHtml(r.title)}</h3><span class="pill">${escapeHtml(r.level)}</span><p class="company">${escapeHtml(r.company)}</p><div>${pills(r.skills)}</div><p class="muted">Connected people: ${(r.people || []).map(escapeHtml).join(', ') || '—'}</p></article>`).join('')}</div></div>`;
  } catch (e) {
    resultsEl.innerHTML = `<div class="card error">${escapeHtml(e.message)}</div>`;
  }
});

document.querySelector('#reload').addEventListener('click', loadRoles);
loadHealth();
loadRoles();
