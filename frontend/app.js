const API_BASE = window.BRANDSCAN_API_BASE || (location.port === '8010' ? '' : 'http://127.0.0.1:8010');
const form = document.querySelector('#analyze-form');
const statusEl = document.querySelector('#status');
const results = document.querySelector('#results');
const resultUrl = document.querySelector('#result-url');
const analysisMeta = document.querySelector('#analysis-meta');
const summaryCards = document.querySelector('#summary-cards');
const priorityList = document.querySelector('#priority-list');
const reviewList = document.querySelector('#review-list');
const detailPanels = document.querySelector('#detail-panels');
const reportButton = document.querySelector('#download-report');
let latestResult = null;

const labels = { confirmed: '확인', partial: '일부 확인', suspicious: '의심', unknown: '미확인' };
const priorityLabels = { high: '높음', medium: '중간', low: '낮음' };
const areaLabels = { martech: 'MarTech', technical_seo: 'Technical SEO', geo: 'GEO · 콘텐츠' };
const objectiveLabels = { brand_awareness: '브랜드 인지도', acquisition: '신규 고객 유입', conversion: '구매 전환', lead_generation: '리드 확보' };
const pageTypeLabels = { homepage: '홈페이지', service: '서비스', product: '상품', landing: '랜딩', blog: '블로그', article: '아티클', campaign: '캠페인', unknown: '미분류' };

function esc(value) {
  return String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
}

function scoreFor(result, area) {
  const count = result.issues.filter(issue => issue.area === area).length;
  return Math.max(38, 100 - count * 18);
}

function scoreTone(score) { return score >= 75 ? 'good' : score >= 55 ? 'warn' : 'bad'; }

function renderSummary(result) {
  const seo = result.technical_seo;
  const tools = result.martech.tools;
  const martechConfirmed = Object.values(tools).filter(tool => tool.status === 'confirmed').length;
  const geoConfirmed = [result.geo.has_question_heading, result.geo.has_explanatory_content, result.geo.has_faq_schema].filter(Boolean).length;
  const cards = [
    { title: 'MarTech · 트래킹', score: scoreFor(result, 'martech'), note: `스크립트 ${martechConfirmed}개 감지 · 확인 상태와 미확인 항목 분리`, area: 'martech' },
    { title: 'Technical SEO', score: scoreFor(result, 'technical_seo'), note: `H1 ${seo.headings.h1.length}개 · 이미지 alt 누락 ${seo.images.missing_alt}개`, area: 'technical_seo' },
    { title: 'GEO · 콘텐츠', score: scoreFor(result, 'geo'), note: `${geoConfirmed}/3 요소 확인 · 질문형·설명형·FAQ 구조`, area: 'geo' },
  ];
  summaryCards.innerHTML = cards.map(card => `<article class="summary">
    <div class="summary-head"><h3>${esc(card.title)}</h3><div class="score ${scoreTone(card.score)}">${card.score}</div></div>
    <div class="bar"><span class="${scoreTone(card.score)}" style="width:${card.score}%"></span></div>
    <p>${esc(card.note)}</p>
  </article>`).join('');
}

function renderPriorities(items) {
  priorityList.innerHTML = items.map((item, index) => `<article class="issue" role="button" tabindex="0" aria-expanded="false" data-index="${index}">
    <div class="rank">${index + 1}</div>
    <div><h3>${esc(item.title)} <span class="chevron">⌄</span></h3>
      <p class="issue-hint">클릭해서 문제의 근거와 개선 방향 보기</p>
      <div class="issue-detail"><p><b>문제점</b> · ${esc(item.problem)}</p><p><b>발견 근거</b> · ${esc(item.evidence)}</p><p><b>개선 방향</b> · ${esc(item.recommendation)}</p><p><b>산정 근거</b> · ${esc(item.score_reason)}</p></div>
    </div>
    <div class="priority ${item.priority === 'high' ? 'p1' : 'p2'}">${esc(priorityLabels[item.priority] || item.priority)} · ${esc(areaLabels[item.area] || item.area)}</div>
  </article>`).join('');
  priorityList.querySelectorAll('.issue').forEach(issue => {
    const toggle = () => {
      const open = issue.classList.toggle('open');
      issue.setAttribute('aria-expanded', String(open));
      const item = items[Number(issue.dataset.index)];
      switchTab(item.area);
    };
    issue.addEventListener('click', toggle);
    issue.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); toggle(); } });
  });
}

function renderAdditionalReview(items) {
  reviewList.hidden = items.length === 0;
  reviewList.innerHTML = items.length ? `<div class="review-heading"><strong>추가 검증 필요 항목</strong><span>확정된 개선 과제와 분리</span></div>${items.map(item => `<div class="review-row"><span class="review-status">추가 검증 필요</span><strong>${esc(item.title)}</strong><span>${esc(item.evidence)}</span></div>`).join('')}` : '';
}

function stateRow(label, status) {
  const safeStatus = labels[status] || status;
  const tone = status === 'confirmed' ? 'ok' : status === 'unknown' ? 'na' : 'warn';
  return `<li><span class="state"><i class="dot ${tone}"></i>${esc(label)} · ${esc(safeStatus)}</span></li>`;
}

function renderPanels(result) {
  const tools = result.martech.tools;
  const seo = result.technical_seo;
  const geo = result.geo;
  const geoIssues = result.issues.filter(issue => issue.area === 'geo');
  const geoEvaluation = result.geo_evaluation;
  const geoCriteria = geoEvaluation.criteria.map(item => `<div><b>${esc(item.criterion_id)}</b>${esc(item.result)} · ${esc(item.reason)}<br><small>근거: ${esc(item.evidence_refs.join(', '))}</small></div>`).join('');
  detailPanels.innerHTML = `
    <div id="panel-all" class="panel" role="tabpanel"><div class="detail-grid">
      <div class="detail"><h4>MarTech 확인 상태</h4><ul>${Object.entries(tools).map(([name, data]) => stateRow(name.replace('_', ' ').toUpperCase(), data.status)).join('')}</ul></div>
      <div class="detail"><h4>SEO 핵심 상태</h4><ul>${stateRow('Title', seo.title ? 'confirmed' : 'unknown')}${stateRow('Meta Description', seo.description ? 'confirmed' : 'partial')}${stateRow('Canonical', seo.canonical ? 'confirmed' : 'unknown')}${stateRow('JSON-LD', seo.json_ld_types.length ? 'confirmed' : 'unknown')}</ul></div>
      <div class="detail"><h4>GEO 콘텐츠 상태</h4><ul>${stateRow('질문형 heading', geo.has_question_heading ? 'confirmed' : 'unknown')}${stateRow('설명형 콘텐츠', geo.has_explanatory_content ? 'confirmed' : 'unknown')}${stateRow('FAQ Schema', geo.has_faq_schema ? 'confirmed' : 'unknown')}</ul></div>
    </div></div>
    <div id="panel-martech" class="panel" role="tabpanel" hidden><div class="detail-note"><strong>MarTech·트래킹 체크리스트</strong><br>설치 스크립트 감지와 실제 추적 요청을 분리합니다. 확인하지 못한 항목은 실패가 아니라 <strong>미확인</strong>으로 표시합니다.</div><div class="checklist">${Object.entries(tools).map(([name, data]) => `<div class="check-row"><span class="check-box ${data.status === 'confirmed' ? 'ok' : data.status === 'unknown' ? 'na' : 'warn'}">${data.status === 'confirmed' ? '✓' : data.status === 'unknown' ? '?' : '!'}</span><span>${esc(name.replace('_', ' ').toUpperCase())} 스크립트 단서</span><span class="check-status">${esc(labels[data.status] || data.status)}</span></div>`).join('')}</div><p class="check-caption">상태 기준 · 확인: 공개 HTML에서 단서 감지 · 일부 확인/의심: 추가 검증 필요 · 미확인: 공개 페이지에서 판단할 수 없음</p><div class="media-list"><h3>탐지된 매체·태그 단서</h3>${result.martech.media_inventory.length ? result.martech.media_inventory.map(item => `<div class="media-row"><strong>${esc(item.platform)}</strong><span>${esc(item.category)}</span><em>운영 중</em><small>${esc(item.evidence.join(', '))}</small></div>`).join('') : '<p class="check-caption">공개 HTML에서 알려진 매체 태그 단서를 찾지 못했습니다.</p>'}</div><p class="check-caption">주의: 이 목록은 공개 HTML에서 태그 단서가 확인된 매체 목록이며, 실제 캠페인 운영·광고비·성과를 의미하지 않습니다.</p></div>
    <div id="panel-technical_seo" class="panel" role="tabpanel" hidden><div class="detail-note"><strong>Technical SEO 상세</strong><br>페이지 HTML에서 직접 확인한 구조적 신호입니다. 검색 순위·트래픽·색인 성과를 측정한 결과가 아닙니다.</div><div class="evidence"><div><b>Title</b>${esc(seo.title || '미확인')}</div><div><b>Meta Description</b>${esc(seo.description || '미확인')}</div><div><b>H1~H3</b>H1 ${seo.headings.h1.length}개 · H2 ${seo.headings.h2.length}개 · H3 ${seo.headings.h3.length}개</div><div><b>이미지 alt</b>전체 ${seo.images.total}개 · 누락 ${seo.images.missing_alt}개</div><div><b>Canonical</b>${esc(seo.canonical || '미확인')}</div><div><b>JSON-LD</b>${seo.json_ld_types.length ? esc(seo.json_ld_types.join(', ')) : '미검출'}</div></div></div>
    <div id="panel-geo" class="panel" role="tabpanel" hidden><div class="detail-note"><strong>GEO 준비도 · ${esc(geoEvaluation.geo_readiness.status)}</strong><br>AI 검색 노출·인용 성과는 측정하지 않았습니다. 현재 결과는 공개 페이지 구조와 근거 문장을 평가한 것입니다.</div><div class="evidence">${geoCriteria}</div><div class="recommend-grid">${geoIssues.length ? geoIssues.map((issue, i) => `<div class="recommend"><h4>소재 ${i + 1} · ${esc(issue.title)}</h4><p><strong>개선 방향</strong> · ${esc(issue.recommendation)}</p><div class="copy-example"><span class="copy-label">근거</span>${esc(issue.evidence)}</div></div>`).join('') : '<div class="recommend"><h4>현재 확인된 GEO 개선 과제 없음</h4><p>추가 확인이 필요한 콘텐츠 구조를 계속 점검합니다.</p></div>'}</div></div>`;
  document.querySelectorAll('.tab').forEach(tab => tab.addEventListener('click', () => switchTab(tab.dataset.tab)));
}

function switchTab(name) {
  document.querySelectorAll('.tab').forEach(tab => { const active = tab.dataset.tab === name; tab.classList.toggle('active', active); tab.setAttribute('aria-selected', String(active)); });
  const panelName = name === 'seo' ? 'technical_seo' : name;
  document.querySelectorAll('.panel').forEach(panel => { panel.hidden = panel.id !== `panel-${panelName}`; });
}

form.addEventListener('submit', async event => {
  event.preventDefault();
  const url = new FormData(form).get('url');
  const formData = new FormData(form);
  const marketingObjective = formData.get('marketing_objective');
  const pageType = formData.get('page_type');
  statusEl.textContent = '페이지를 분석하고 있습니다...'; statusEl.className = 'status loading'; results.hidden = true;
  try {
    const response = await fetch(`${API_BASE}/api/analyze`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({url, marketing_objective: marketingObjective, page_type: pageType || null}) });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || '분석에 실패했습니다.');
    latestResult = payload; resultUrl.textContent = payload.final_url; const context = payload.analysis_metadata; analysisMeta.textContent = `HTTP ${payload.status_code} · HTML ${payload.html_size.toLocaleString()} bytes · ${pageTypeLabels[context.page_type.selected] || context.page_type.selected} · ${objectiveLabels[context.marketing_objective] || context.marketing_objective}`;
    renderSummary(payload); renderPriorities(payload.top_priorities); renderAdditionalReview(payload.additional_review_items); renderPanels(payload); switchTab('all'); results.hidden = false;
    statusEl.textContent = '분석이 완료되었습니다.'; statusEl.className = 'status success';
  } catch (error) { statusEl.textContent = error.message; statusEl.className = 'status error'; }
});

reportButton.addEventListener('click', () => { if (latestResult) window.print(); });
