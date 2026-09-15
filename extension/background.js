const DEFAULT_BASE_URL = "http://localhost:8000";

async function getBaseUrl() {
  const { backendUrl } = await chrome.storage.local.get("backendUrl");
  return backendUrl || DEFAULT_BASE_URL;
}

async function apiMatch(jobText, jobUrl, jobTitle) {
  const baseUrl = await getBaseUrl();
  const res = await fetch(`${baseUrl}/api/match`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ job_text: jobText, job_url: jobUrl, job_title: jobTitle }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Ошибка сервера: ${res.status}`);
  }
  return res.json();
}

async function apiGetProfile() {
  const baseUrl = await getBaseUrl();
  const res = await fetch(`${baseUrl}/api/profile`);
  if (!res.ok) {
    throw new Error("Не удалось получить профиль. Проверьте, что бэкенд запущен");
  }
  return res.json();
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.type === "MATCH_JOB") {
    apiMatch(message.jobText, message.jobUrl, message.jobTitle)
      .then((data) => sendResponse({ ok: true, data }))
      .catch((err) => sendResponse({ ok: false, error: err.message }));
    return true;
  }
  if (message.type === "GET_PROFILE") {
    apiGetProfile()
      .then((data) => sendResponse({ ok: true, data }))
      .catch((err) => sendResponse({ ok: false, error: err.message }));
    return true;
  }
  return false;
});
