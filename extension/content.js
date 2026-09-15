const JOB_KEYWORDS = [
  "responsibilities",
  "requirements",
  "qualifications",
  "обязанности",
  "требования",
  "условия",
  "вакансия",
  "зарплата",
];

function looksLikeJobPage() {
  const text = document.body.innerText.toLowerCase();
  let hits = 0;
  for (const kw of JOB_KEYWORDS) {
    if (text.includes(kw)) hits++;
  }
  return hits >= 2 && text.length > 500;
}

function extractJobText() {
  const candidates = [
    "[class*='description']",
    "[class*='vacancy']",
    "[class*='job']",
    "article",
    "main",
  ];
  for (const sel of candidates) {
    const el = document.querySelector(sel);
    if (el && el.innerText && el.innerText.length > 300) {
      return el.innerText;
    }
  }
  return document.body.innerText;
}

function createOverlay() {
  const el = document.createElement("div");
  el.id = "jobrate-overlay";
  el.innerHTML = `
    <div id="jobrate-header">
      <span>JobRate</span>
      <button id="jobrate-close" title="Закрыть">×</button>
    </div>
    <div id="jobrate-body">Анализируем вакансию...</div>
  `;
  document.body.appendChild(el);
  el.querySelector("#jobrate-close").addEventListener("click", () => el.remove());
  return el;
}

function badge(text, kind) {
  return `<span class="jobrate-badge jobrate-badge-${kind}">${text}</span>`;
}

function renderResult(el, data) {
  const body = el.querySelector("#jobrate-body");
  const matchedHtml = data.matched_skills.map((s) => badge(s, "ok")).join("") || "—";
  const missingHtml = data.missing_skills.map((s) => badge(s, "missing")).join("") || "—";

  body.innerHTML = `
    <div class="jobrate-percent">${data.match_percent}%</div>
    <p class="jobrate-summary">${data.summary}</p>
    <div class="jobrate-section-title">Есть у вас</div>
    <div class="jobrate-badges">${matchedHtml}</div>
    <div class="jobrate-section-title">Не хватает</div>
    <div class="jobrate-badges">${missingHtml}</div>
  `;
}

function renderError(el, message) {
  el.querySelector("#jobrate-body").innerHTML = `<p class="jobrate-error">${message}</p>`;
}

(async function init() {
  if (!looksLikeJobPage()) return;

  const profileResp = await chrome.runtime.sendMessage({ type: "GET_PROFILE" });
  if (!profileResp.ok || !profileResp.data.skills || profileResp.data.skills.length === 0) {
    return; // профиль не заполнен — виджет не показываем
  }

  const overlay = createOverlay();
  const jobText = extractJobText();

  const result = await chrome.runtime.sendMessage({
    type: "MATCH_JOB",
    jobText,
    jobUrl: location.href,
    jobTitle: document.title,
  });

  if (result.ok) {
    renderResult(overlay, result.data);
  } else {
    renderError(overlay, result.error);
  }
})();
