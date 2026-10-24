const API_BASE = window.BRANDSCAN_API_BASE || (location.port === '8010' ? '' : 'http://127.0.0.1:8010');
const form = document.querySelector('#analyze-form');
const statusEl = document.querySelector('#status');
const results = document.querySelector('#results');
const resultUrl = document.querySelector('#result-url');
const summaryCards = document.querySelector('#summary-cards');
const priorityList = document.querySelector('#priority-list');
const detail = document.querySelector('#detail');
const reportButton = document.querySelector('#download-report');
let latestResult = null;

const labels = {
  confirmed: '확인',
  partial: '일부 확인',
  suspicious: '의심',
  unknown: '미확인',
};

function esc(value) {
  return String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
}

function renderSummary(result) {
  const seo = result.technical_seo;
  const tools = result.martech.tools;
  const martechConfirmed = Object.values(tools).filter(tool => tool.status === 'confirmed').length;
  const geoConfirmed = [result.geo.has_question_heading, result.geo.has_explanatory_content, result.geo.has_faq_schema].filter(Boolean).length;
  summaryCards.innerHTML = [
    ['Technical SEO', seo.description && seo.title ? '기본 요소 확인' : '개선 필요', `${seo.headings.h1.length}개 H1 · alt 누락 ${seo.images.missing_alt}개`],
    ['MarTech', martechConfirmed ? `${martechConfirmed}개 감지` : '추가 확인 필요', '스크립트 단서 기준'],
    ['GEO', `${geoConfirmed}/3 요소 확인`, '질문형·설명형·FAQ 구조'],
  ].map(([title, value, note]) => `<article class="summary-card"><p>${esc(title)}</p><strong>${esc(value)}</strong><span>${esc(note)}</span></article>`).join('');
}

function renderPriorities(items) {
  priorityList.innerHTML = items.map((item, index) => `<button class="priority-card" data-index="${index}" type="button">
    <span class="priority-number">0${index + 1}</span>
    <span class="priority-area">${esc(item.area)}</span>
    <h3>${esc(item.title)}</h3>
    <span class="priority-status status-${esc(item.status)}">${esc(labels[item.status] || item.status)}</span>
    <p>${esc(item.evidence)}</p>
  </button>`).join('');
  priorityList.querySelectorAll('.priority-card').forEach(card => card.addEventListener('click', () => showDetail(items[Number(card.dataset.index)])));
}

function showDetail(item) {
  detail.hidden = false;
  detail.innerHTML = `<p class="eyebrow">EVIDENCE DETAIL</p><h2>${esc(item.title)}</h2>
    <dl><dt>상태</dt><dd>${esc(labels[item.status] || item.status)}</dd><dt>발견 근거</dt><dd>${esc(item.evidence)}</dd><dt>개선 방향</dt><dd>${esc(item.recommendation)}</dd><dt>우선순위 산정</dt><dd>${esc(item.score_reason)}</dd></dl>`;
  detail.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

form.addEventListener('submit', async event => {
  event.preventDefault();
  const url = new FormData(form).get('url');
  statusEl.textContent = '페이지를 분석하고 있습니다...';
  statusEl.className = 'status loading';
  results.hidden = true;
  try {
    const response = await fetch(`${API_BASE}/api/analyze`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({url}) });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || '분석에 실패했습니다.');
    latestResult = payload;
    resultUrl.textContent = payload.final_url;
    renderSummary(payload);
    renderPriorities(payload.top_priorities);
    detail.hidden = true;
    results.hidden = false;
    statusEl.textContent = '분석이 완료되었습니다.';
    statusEl.className = 'status success';
  } catch (error) {
    statusEl.textContent = error.message;
    statusEl.className = 'status error';
  }
});

reportButton.addEventListener('click', () => {
  if (!latestResult) return;
  window.print();
  return;
});
/*
  const blob = new Blob([printable], {type: 'text/plain;charset=utf-8'});
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = 'brandscan-report.txt';
  link.click();
*/
