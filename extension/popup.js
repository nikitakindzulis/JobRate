const DEFAULT_BASE_URL = "http://localhost:8000";

async function getBaseUrl() {
  const { backendUrl } = await chrome.storage.local.get("backendUrl");
  return backendUrl || DEFAULT_BASE_URL;
}

function renderSkills(skills) {
  const list = document.getElementById("skills-list");
  list.innerHTML = "";
  skills.forEach((s) => {
    const li = document.createElement("li");
    const label = document.createElement("span");
    label.textContent = s.name + (s.level && s.level !== "unknown" ? ` (${s.level})` : "");
    const del = document.createElement("button");
    del.textContent = "×";
    del.title = "Удалить";
    del.addEventListener("click", () => removeSkill(s.name, skills));
    li.appendChild(label);
    li.appendChild(del);
    list.appendChild(li);
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
    if (!res.ok) throw new Error("Сервер недоступен");
    const data = await res.json();
    renderSkills(data.skills);
    document.getElementById("summary").textContent = data.summary || "";
    statusEl.textContent = "";
  } catch (e) {
    statusEl.textContent = `Бэкенд недоступен: ${e.message}`;
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
  if (!file) return;

  const statusEl = document.getElementById("status");
  statusEl.textContent = "Анализируем резюме...";

  const baseUrl = await getBaseUrl();
  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch(`${baseUrl}/api/cv`, { method: "POST", body: formData });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Ошибка ${res.status}`);
    }
    const data = await res.json();
    renderSkills(data.skills);
    document.getElementById("summary").textContent = data.summary || "";
    statusEl.textContent = "Готово!";
  } catch (err) {
    statusEl.textContent = `Ошибка: ${err.message}`;
  }
});

document.getElementById("backend-url").addEventListener("change", async (e) => {
  await chrome.storage.local.set({ backendUrl: e.target.value });
});

(async function initPopup() {
  document.getElementById("backend-url").value = await getBaseUrl();
  await loadProfile();
})();
