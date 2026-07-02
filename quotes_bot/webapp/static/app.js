const tg = window.Telegram?.WebApp;
let initData = "";
let profile = null;
let packs = [];

function refreshInitData() {
  initData = tg?.initData || window.Telegram?.WebApp?.initData || "";
  return initData;
}

function apiUrl(path) {
  refreshInitData();
  if (!initData) return path;
  const sep = path.includes("?") ? "&" : "?";
  return `${path}${sep}initData=${encodeURIComponent(initData)}`;
}

function api(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    "X-Telegram-Init-Data": refreshInitData(),
    ...(options.headers || {}),
  };
  return fetch(apiUrl(path), { ...options, headers }).then(async (res) => {
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || data.message || "Request failed");
    return data;
  });
}

function cardImageUrl(card, isNew = false) {
  refreshInitData();
  const params = new URLSearchParams();
  if (isNew) params.set("new", "1");
  if (initData) params.set("initData", initData);
  const qs = params.toString();
  return qs ? `${card.image_url}?${qs}` : card.image_url;
}

function updateStats(nextProfile) {
  profile = nextProfile;
  document.getElementById("tickets").textContent = nextProfile.tickets;
  document.getElementById("dust").textContent = nextProfile.duplicate_dust;
  document.getElementById("cards").textContent = `${nextProfile.cards_owned}/${nextProfile.total_cards}`;
  document.getElementById("exchange-dust").textContent = nextProfile.duplicate_dust;
}

function showToast(text) {
  const el = document.getElementById("toast");
  el.textContent = text;
  el.classList.remove("hidden");
  setTimeout(() => el.classList.add("hidden"), 3200);
}

function showPackError(text) {
  const root = document.getElementById("pack-list");
  root.innerHTML = `<p class="empty error">${text}</p>`;
}

function renderPacks() {
  const root = document.getElementById("pack-list");
  root.innerHTML = "";
  if (!packs.length) {
    root.innerHTML = '<p class="empty">Паки не найдены</p>';
    return;
  }
  for (const pack of packs) {
    const card = document.createElement("div");
    card.className = "pack-card";
    if ((profile?.tickets || 0) < 1) card.classList.add("disabled");
    card.innerHTML = `
      <div class="pack-head">
        <div class="pack-name">${pack.emoji} ${pack.name}</div>
        <div class="pack-progress">${pack.owned}/${pack.total}</div>
      </div>
      <p class="pack-desc">${pack.description}</p>
      <div class="pack-members">${pack.members.join(" · ")}</div>
    `;
    card.addEventListener("click", () => openPack(pack));
    root.appendChild(card);
  }
}

async function openPack(pack) {
  if ((profile?.tickets || 0) < 1) {
    showToast("Не хватает билетов 🎫");
    return;
  }
  const overlay = document.getElementById("overlay");
  const title = document.getElementById("overlay-title");
  const reveal = document.getElementById("reveal-cards");
  overlay.classList.remove("hidden");
  title.textContent = `${pack.emoji} Открываем ${pack.name}…`;
  reveal.innerHTML = '<p class="empty">Тасуем карты…</p>';

  try {
    const data = await api(`/api/packs/${pack.id}/open`, { method: "POST" });
    updateStats(data.profile);
    title.textContent = `✅ ${pack.name}: ✨ ${data.new_count} · 🔁 ${data.duplicate_count}`;
    reveal.innerHTML = data.cards
      .map(
        (card) => `
          <div>
            <img src="${cardImageUrl(card, card.is_new)}" alt="${card.person_name}" />
            <div class="card-caption">${card.is_new ? "✨ NEW" : "🔁 DUP"} · ${card.person_name}</div>
          </div>
        `
      )
      .join("");
    renderPacks();
    tg?.HapticFeedback?.notificationOccurred("success");
  } catch (err) {
    title.textContent = "Ошибка";
    reveal.innerHTML = `<p class="empty">${err.message}</p>`;
    tg?.HapticFeedback?.notificationOccurred("error");
  }
}

async function loadPacks() {
  const data = await api("/api/packs");
  packs = data.packs;
  updateStats(data.profile);
  renderPacks();
}

async function loadCollection() {
  const data = await api("/api/collection");
  updateStats(data.profile);
  const peopleRoot = document.getElementById("collection-people");
  const cardsRoot = document.getElementById("collection-cards");
  peopleRoot.innerHTML = data.people.length
    ? data.people.map((p) => `<span class="chip">${p.name} ${p.owned}/${p.total}</span>`).join("")
    : '<p class="empty">Коллекция пуста. Открой пак!</p>';
  cardsRoot.innerHTML = data.cards.length
    ? data.cards
        .slice(0, 40)
        .map(
          (card) => `
            <div class="card-thumb">
              <img src="${cardImageUrl(card)}" alt="${card.person_name}" loading="lazy" />
              <div class="card-caption">${card.person_name}</div>
            </div>
          `
        )
        .join("")
    : "";
}

async function loadLeaderboard() {
  const data = await api("/api/leaderboard");
  const root = document.getElementById("leaderboard");
  if (!data.entries.length) {
    root.innerHTML = '<p class="empty">Пока никто не собрал карточки</p>';
    return;
  }
  root.innerHTML = data.entries
    .map(
      (entry) => `
        <div class="leader-row ${entry.is_you ? "you" : ""}">
          <div>
            <div class="leader-name">${entry.rank <= 3 ? ["🥇", "🥈", "🥉"][entry.rank - 1] : entry.rank + "."} ${entry.display_name}</div>
            <div class="leader-meta">${entry.is_you ? "это ты · " : ""}📦 ${entry.packs_opened} паков</div>
          </div>
          <div class="leader-meta">📚 ${entry.cards_owned}</div>
        </div>
      `
    )
    .join("");
  if (data.your_rank) {
    root.innerHTML += `<p class="message">Твоё место: #${data.your_rank}</p>`;
  }
}

async function exchangeTicket() {
  try {
    const data = await api("/api/exchange/ticket", { method: "POST" });
    updateStats(data.profile);
    document.getElementById("exchange-message").textContent = data.message.replace(/<[^>]+>/g, "");
    renderPacks();
    tg?.HapticFeedback?.impactOccurred("medium");
  } catch (err) {
    showToast(err.message);
  }
}

async function exchangeCard() {
  try {
    const data = await api("/api/exchange/card", { method: "POST" });
    updateStats(data.profile);
    document.getElementById("exchange-message").textContent = data.message.replace(/<[^>]+>/g, "");
    if (data.card) {
      const overlay = document.getElementById("overlay");
      const reveal = document.getElementById("reveal-cards");
      document.getElementById("overlay-title").textContent = "✨ Новая карта из обмена";
      reveal.innerHTML = `<img src="${cardImageUrl(data.card, true)}" alt="${data.card.person_name}" />`;
      overlay.classList.remove("hidden");
    }
    tg?.HapticFeedback?.notificationOccurred("success");
  } catch (err) {
    showToast(err.message);
  }
}

function switchTab(name) {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.tab === name);
  });
  document.querySelectorAll(".panel").forEach((panel) => {
    panel.classList.toggle("active", panel.id === `tab-${name}`);
  });
}

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", async () => {
    const name = tab.dataset.tab;
    switchTab(name);
    try {
      if (name === "packs") await loadPacks();
      if (name === "collection") await loadCollection();
      if (name === "leaders") await loadLeaderboard();
    } catch (err) {
      showToast(err.message);
      if (name === "packs") showPackError(err.message);
    }
  });
});

document.getElementById("btn-exchange-ticket").addEventListener("click", exchangeTicket);
document.getElementById("btn-exchange-card").addEventListener("click", exchangeCard);
document.getElementById("overlay-close").addEventListener("click", () => {
  document.getElementById("overlay").classList.add("hidden");
});

async function boot() {
  tg?.ready();
  tg?.expand();
  tg?.setHeaderColor("#0f1014");
  tg?.setBackgroundColor("#0f1014");
  refreshInitData();

  if (!initData) {
    showPackError("Открой Mini App через кнопку 🎮 Играть в боте");
    showToast("Нет Telegram initData");
    return;
  }

  try {
    await loadPacks();
  } catch (err) {
    showPackError(err.message);
    showToast(err.message);
  }
}

boot();
