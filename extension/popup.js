const DEFAULT_BASE_URL = "http://localhost:8000";

async function getBaseUrl() {
  const { backendUrl } = await chrome.storage.local.get("backendUrl");
  return backendUrl || DEFAULT_BASE_URL;
}

function renderSkills(skills) {
  const list = document.getElementById("skills-list");
  list.innerHTML = "";
  skills.forEach((s) => {
    const chip = document.createElement("div");
    chip.className = "skill-chip";

    const label = document.createElement("span");
    label.textContent = s.name + (s.level && s.level !== "unknown" ? ` (${s.level})` : "");

    const del = document.createElement("button");
    del.textContent = "×";
    del.title = "Remove";
    del.addEventListener("click", () => removeSkill(s.name, skills));

    chip.appendChild(label);
    chip.appendChild(del);
    list.appendChild(chip);
  });
}

async function saveSkills(names) {
  const baseUrl = await getBaseUrl();
  const res = await fetch(`${baseUrl}/api/profile`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ skills: names }),
  });
  const data = await res.json();
  renderSkills(data.skills);
}

async function removeSkill(name, currentSkills) {
  const remaining = currentSkills.filter((s) => s.name !== name).map((s) => s.name);
  await saveSkills(remaining);
}

async function loadProfile() {
  const statusEl = document.getElementById("status");
  const baseUrl = await getBaseUrl();
  try {
    const res = await fetch(`${baseUrl}/api/profile`);
    if (!res.ok) throw new Error("Server unavailable");
    const data = await res.json();
    renderSkills(data.skills);
    document.getElementById("summary").textContent = data.summary || "";
    statusEl.textContent = "";
  } catch (e) {
    statusEl.textContent = `Backend unavailable: ${e.message}`;
  }
}

document.getElementById("add-skill-btn").addEventListener("click", async () => {
  const input = document.getElementById("new-skill");
  const name = input.value.trim();
  if (!name) return;
  const baseUrl = await getBaseUrl();
  const res = await fetch(`${baseUrl}/api/profile`);
  const data = await res.json();
  const names = data.skills.map((s) => s.name);
  names.push(name);
  await saveSkills(names);
  input.value = "";
});

document.getElementById("cv-upload").addEventListener("change", async (e) => {
  const file = e.target.files[0];
  document.getElementById("file-name").textContent = file ? file.name : "No file chosen";
  if (!file) return;

  const statusEl = document.getElementById("status");
  statusEl.textContent = "Analyzing resume...";

  const baseUrl = await getBaseUrl();
  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch(`${baseUrl}/api/cv`, { method: "POST", body: formData });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Error ${res.status}`);
    }
    const data = await res.json();
    renderSkills(data.skills);
    document.getElementById("summary").textContent = data.summary || "";
    statusEl.textContent = "Done!";
  } catch (err) {
    statusEl.textContent = `Error: ${err.message}`;
  }
});

document.getElementById("backend-url").addEventListener("change", async (e) => {
  await chrome.storage.local.set({ backendUrl: e.target.value });
});

async function injectContentScript(tabId) {
  await chrome.scripting.insertCSS({ target: { tabId }, files: ["overlay.css"] });
  await chrome.scripting.executeScript({ target: { tabId }, files: ["content.js"] });
}

document.getElementById("analyze-btn").addEventListener("click", async () => {
  const statusEl = document.getElementById("status");
  statusEl.textContent = "Sending analysis request...";
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab?.id) throw new Error("Could not determine the active tab");

    try {
      await chrome.tabs.sendMessage(tab.id, { type: "FORCE_ANALYZE" });
    } catch (e) {
      // Content script isn't injected into this tab yet (e.g. the page was
      // open before the extension was reloaded) — inject it and retry.
      await injectContentScript(tab.id);
      await chrome.tabs.sendMessage(tab.id, { type: "FORCE_ANALYZE" });
    }

    statusEl.textContent = "Done — the result will appear as a widget on the job page.";
  } catch (e) {
    console.error("JobRate analyze-btn error:", e);
    statusEl.textContent = `Error: ${e.message || e}`;
  }
});

(async function initPopup() {
  document.getElementById("backend-url").value = await getBaseUrl();
  await loadProfile();
})();
