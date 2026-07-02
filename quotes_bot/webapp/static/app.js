const tg = window.Telegram?.WebApp;
let initData = "";
let tgUser = null;
let profile = null;
let packs = [];

let revealState = null;
let tradeState = {
  myCards: [],
  partnerCards: [],
  selectedOfferId: null,
  selectedRequestId: null,
  incoming: [],
  outgoing: [],
  acceptGiveByTrade: {},
};

function refreshInitData() {
  initData = tg?.initData || window.Telegram?.WebApp?.initData || "";
  tgUser = tg?.initDataUnsafe?.user || null;
  return initData;
}

function authBody(extra = {}) {
  refreshInitData();
  return JSON.stringify({
    initData,
    user: tgUser,
    ...extra,
  });
}

function api(path, options = {}) {
  refreshInitData();
  const method = options.method || "POST";
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  if (initData) {
    headers.Authorization = `tma ${initData}`;
  }

  const body =
    method === "GET"
      ? undefined
      : authBody(typeof options.body === "object" ? options.body : {});

  return fetch(path, { ...options, method, headers, body })
    .catch(() => {
      throw new Error("Сервер недоступен. Закрой Mini App и открой снова через 🎮 Играть");
    })
    .then(async (res) => {
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.error || data.message || `Ошибка сервера (${res.status})`);
      }
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

function rarityTag(card, { inline = false } = {}) {
  const cls = inline ? "rarity-tag rarity-inline" : "rarity-tag";
  return `<span class="${cls} rarity-${card.rarity}" style="--rarity-color:${card.rarity_color}">${card.rarity_emoji} ${card.rarity_label}</span>`;
}

function duplicateTag(card) {
  if (!card.is_duplicate && !(card.duplicate_count > 0)) return "";
  const suffix = card.duplicate_count > 1 ? ` ×${card.duplicate_count}` : "";
  return `<span class="dup-tag">🔁 Дубликат${suffix}</span>`;
}

function preloadImage(url) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = url;
  });
}

function updateStats(nextProfile) {
  if (!nextProfile) return;
  profile = nextProfile;
  document.getElementById("tickets").textContent = nextProfile.tickets;
  document.getElementById("dust").textContent = nextProfile.duplicate_dust;
  document.getElementById("cards").textContent = `${nextProfile.cards_owned}/${nextProfile.total_cards}`;
  document.getElementById("exchange-dust").textContent = nextProfile.duplicate_dust;
  updateDustBars(nextProfile.duplicate_dust);
}

function updateDustBars(dust) {
  const ticketBar = document.getElementById("dust-bar-ticket");
  const cardBar = document.getElementById("dust-bar-card");
  if (ticketBar) ticketBar.style.width = `${Math.min(100, (dust / 3) * 100)}%`;
  if (cardBar) cardBar.style.width = `${Math.min(100, (dust / 5) * 100)}%`;
}

function animateDustGain(amount = 1) {
  const dustEl = document.getElementById("dust");
  dustEl.classList.add("dust-pulse");
  setTimeout(() => dustEl.classList.remove("dust-pulse"), 700);

  const float = document.createElement("div");
  float.className = "dust-float";
  float.textContent = `+${amount} 🔁`;
  document.body.appendChild(float);
  setTimeout(() => float.remove(), 1200);
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

function getRevealElements() {
  return {
    overlay: document.getElementById("overlay"),
    title: document.getElementById("overlay-title"),
    progress: document.getElementById("reveal-progress"),
    opening: document.getElementById("opening-animation"),
    slot: document.getElementById("reveal-card-slot"),
    summary: document.getElementById("reveal-summary"),
    btnNext: document.getElementById("overlay-next"),
    btnClose: document.getElementById("overlay-close"),
  };
}

function resetRevealUI() {
  const el = getRevealElements();
  el.opening.classList.remove("hidden");
  el.slot.classList.add("hidden");
  el.slot.innerHTML = "";
  el.summary.classList.add("hidden");
  el.summary.textContent = "";
  el.progress.textContent = "";
  el.btnNext.classList.add("hidden");
  el.btnClose.classList.add("hidden");
}

function closeReveal() {
  revealState = null;
  document.getElementById("overlay").classList.add("hidden");
  resetRevealUI();
}

function showRevealCard(card, index, total) {
  const el = getRevealElements();
  el.opening.classList.add("hidden");
  el.slot.classList.remove("hidden");
  el.summary.classList.add("hidden");

  const isDup = !card.is_new;
  const badge = card.is_new ? "✨ NEW" : "💨 РАСПЫЛЕНО";
  const badgeClass = card.is_new ? "new" : "dup";

  el.progress.textContent = total > 1 ? `Карта ${index + 1} из ${total}` : "";
  el.title.textContent = card.is_new ? "✨ Новая карта!" : "💨 Дубликат → пыль";

  const dustLine = isDup
    ? `<div class="reveal-dust-gain">+1 пыль 🔁</div>`
    : "";

  el.slot.innerHTML = `
    <div class="reveal-card-frame">
      <div class="reveal-card-inner ${card.is_new ? "is-new" : "is-dup-disintegrate"}">
        <img src="${cardImageUrl(card, card.is_new)}" alt="${card.person_name}" />
      </div>
    </div>
    ${rarityTag(card, { inline: true })}
    <div class="reveal-card-badge ${badgeClass}">${badge}</div>
    <div class="reveal-card-name">${card.person_name}</div>
    ${isDup ? `<div class="reveal-dup-label">${duplicateTag({ ...card, duplicate_count: card.duplicate_count || 1 })}</div>` : ""}
    ${dustLine}
  `;

  if (isDup) {
    animateDustGain(1);
    tg?.HapticFeedback?.notificationOccurred("warning");
  } else {
    tg?.HapticFeedback?.impactOccurred("medium");
  }

  if (index < total - 1) {
    el.btnNext.textContent = "Следующая карта →";
    el.btnNext.classList.remove("hidden");
    el.btnClose.classList.add("hidden");
  } else if (revealState?.packName) {
    el.btnNext.textContent = total > 1 ? "Итоги →" : "Готово";
    el.btnNext.classList.remove("hidden");
    el.btnClose.classList.add("hidden");
  } else {
    el.btnNext.classList.add("hidden");
    el.btnClose.classList.remove("hidden");
  }
}

function showRevealSummary(summaryText) {
  const el = getRevealElements();
  el.slot.classList.add("hidden");
  el.summary.classList.remove("hidden");
  el.summary.textContent = summaryText;
  el.progress.textContent = "";
  el.btnNext.classList.add("hidden");
  el.btnClose.classList.remove("hidden");
}

function advanceReveal() {
  if (!revealState) return;
  if (revealState.index >= revealState.cards.length - 1 && revealState.packName) {
    finishReveal();
    return;
  }
  revealState.index += 1;
  if (revealState.index >= revealState.cards.length) {
    finishReveal();
    return;
  }
  showRevealCard(revealState.cards[revealState.index], revealState.index, revealState.cards.length);
}

function finishReveal() {
  if (!revealState) return;
  revealState.summaryShown = true;
  const { packName, newCount, dupCount, dustGained } = revealState;
  let text = `✅ ${packName}: ✨ ${newCount} · 🔁 ${dupCount}`;
  if (dustGained > 0) text += ` · +${dustGained} пыли`;
  showRevealSummary(text);
  const el = getRevealElements();
  el.title.textContent = "Пак открыт!";
  tg?.HapticFeedback?.notificationOccurred("success");
}

async function startRevealFlow({ title, cards, packName, newCount, dupCount, dustGained }) {
  const el = getRevealElements();
  resetRevealUI();
  el.overlay.classList.remove("hidden");
  el.title.textContent = title;
  el.opening.querySelector(".opening-text").textContent = "Тасуем карты…";

  revealState = {
    cards,
    index: 0,
    summaryShown: false,
    packName: packName || "",
    newCount: newCount ?? cards.filter((c) => c.is_new).length,
    dupCount: dupCount ?? cards.filter((c) => !c.is_new).length,
    dustGained: dustGained ?? 0,
  };

  try {
    await Promise.all(cards.map((c) => preloadImage(cardImageUrl(c, c.is_new))));
  } catch {
    /* show anyway even if preload fails */
  }

  await new Promise((r) => setTimeout(r, 900));
  showRevealCard(cards[0], 0, cards.length);
}

async function openPack(pack) {
  if (!profile && !tgUser) {
    showToast("Не удалось определить игрока. Перезапусти Mini App");
    return;
  }

  const el = getRevealElements();
  resetRevealUI();
  el.overlay.classList.remove("hidden");
  el.title.textContent = `${pack.emoji} Открываем ${pack.name}…`;

  try {
    const data = await api(`/api/packs/${pack.id}/open`, { method: "POST" });
    updateStats(data.profile);
    renderPacks();

    await startRevealFlow({
      title: `${pack.emoji} ${pack.name}`,
      cards: data.cards,
      packName: pack.name,
      newCount: data.new_count,
      dupCount: data.duplicate_count,
      dustGained: data.dust_gained || 0,
    });
  } catch (err) {
    el.opening.classList.add("hidden");
    el.slot.classList.remove("hidden");
    el.slot.innerHTML = `<p class="empty error">${err.message}</p>`;
    el.btnClose.classList.remove("hidden");
    el.title.textContent = "Ошибка";
    tg?.HapticFeedback?.notificationOccurred("error");
  }
}

async function loadPacks() {
  const data = await api("/api/packs", { method: "POST" });
  packs = data.packs || [];
  updateStats(data.profile);
  renderPacks();
}

async function disintegrateCard(quoteId, personName, buttonEl) {
  if (!confirm(`Распылить «${personName}»?\n\nКарта исчезнет из коллекции → +1 пыль 🔁`)) {
    return;
  }
  buttonEl.disabled = true;
  try {
    const data = await api(`/api/cards/${quoteId}/disintegrate`, { method: "POST" });
    updateStats(data.profile);
    animateDustGain(data.dust_gained || 1);
    showToast(`💨 +${data.dust_gained || 1} пыль`);
    tg?.HapticFeedback?.notificationOccurred("success");
    await loadCollection();
  } catch (err) {
    buttonEl.disabled = false;
    showToast(err.message.replace(/<[^>]+>/g, ""));
  }
}

async function loadCollection() {
  const data = await api("/api/collection", { method: "POST" });
  updateStats(data.profile);
  const peopleRoot = document.getElementById("collection-people");
  const cardsRoot = document.getElementById("collection-cards");
  peopleRoot.innerHTML = data.people.length
    ? data.people.map((p) => `<span class="chip">${p.name} ${p.owned}/${p.total}</span>`).join("")
    : '<p class="empty">Коллекция пуста. Открой пак!</p>';

  cardsRoot.innerHTML = "";
  if (!data.cards.length) return;

  for (const card of data.cards.slice(0, 40)) {
    const thumb = document.createElement("div");
    thumb.className = `card-thumb rarity-border rarity-${card.rarity}`;
    thumb.style.setProperty("--rarity-color", card.rarity_color);
    thumb.innerHTML = `
      <div class="card-thumb-media">
        ${rarityTag(card)}
        ${duplicateTag(card)}
        <img src="${cardImageUrl(card)}" alt="${card.person_name}" loading="lazy" />
      </div>
      <div class="card-caption">${card.person_name}</div>
      <button type="button" class="btn-disintegrate">💨 Распылить</button>
    `;
    const btn = thumb.querySelector(".btn-disintegrate");
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      disintegrateCard(card.quote_id, card.person_name, btn);
    });
    cardsRoot.appendChild(thumb);
  }
}

async function loadLeaderboard() {
  const data = await api("/api/leaderboard", { method: "POST" });
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
      await startRevealFlow({
        title: "✨ Новая карта из обмена",
        cards: [{ ...data.card, is_new: true }],
        packName: "Обмен",
        newCount: 1,
        dupCount: 0,
      });
    }
    tg?.HapticFeedback?.notificationOccurred("success");
  } catch (err) {
    showToast(err.message);
  }
}

function switchTradeTab(name) {
  document.querySelectorAll(".trade-subtab").forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.tradeTab === name);
  });
  document.querySelectorAll(".trade-panel").forEach((panel) => {
    panel.classList.toggle("active", panel.id === `trade-panel-${name}`);
  });
}

function updateTradeUsernameHint() {
  const el = document.getElementById("trade-username-hint");
  if (!el) return;
  if (profile?.username) {
    el.textContent = `Ты: @${profile.username}`;
  } else {
    el.textContent = "Задай @username в Telegram";
  }
}

function renderTradeCardPicker(root, cards, { selectedId, onSelect, emptyText }) {
  root.innerHTML = "";
  if (!cards.length) {
    root.classList.add("empty-picker");
    root.innerHTML = `<p class="empty">${emptyText}</p>`;
    return;
  }
  root.classList.remove("empty-picker");
  for (const card of cards) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `trade-pick rarity-border rarity-${card.rarity}${selectedId === card.quote_id ? " selected" : ""}`;
    btn.style.setProperty("--rarity-color", card.rarity_color);
    btn.innerHTML = `
      <img src="${cardImageUrl(card)}" alt="${card.person_name}" loading="lazy" />
      <div class="trade-pick-name">${card.person_name}</div>
    `;
    btn.addEventListener("click", () => onSelect(card.quote_id));
    root.appendChild(btn);
  }
}

function updateTradeCreateButton() {
  const btn = document.getElementById("btn-trade-create");
  const partner = document.getElementById("trade-partner-input")?.value.trim();
  btn.disabled = !(partner && tradeState.selectedOfferId);
}

function renderTradeCreateForm() {
  renderTradeCardPicker(document.getElementById("trade-my-cards"), tradeState.myCards, {
    selectedId: tradeState.selectedOfferId,
    onSelect: (id) => {
      tradeState.selectedOfferId = tradeState.selectedOfferId === id ? null : id;
      renderTradeCreateForm();
      updateTradeCreateButton();
    },
    emptyText: "Нет карт для обмена",
  });

  renderTradeCardPicker(document.getElementById("trade-partner-cards"), tradeState.partnerCards, {
    selectedId: tradeState.selectedRequestId,
    onSelect: (id) => {
      tradeState.selectedRequestId = tradeState.selectedRequestId === id ? null : id;
      renderTradeCreateForm();
    },
    emptyText: "Сначала найди игрока",
  });
  updateTradeCreateButton();
}

function tradeMiniCard(card) {
  if (!card) return `<div class="trade-mini-card"><span>любая карта</span></div>`;
  return `
    <div class="trade-mini-card">
      <img src="${cardImageUrl(card)}" alt="${card.person_name}" />
      <span>${card.person_name}</span>
    </div>
  `;
}

function renderTradeOfferActions(trade) {
  if (trade.is_incoming) {
    const giveId =
      trade.requested_card?.quote_id ||
      tradeState.acceptGiveByTrade[trade.id] ||
      null;

    const givePicker =
      trade.requested_card
        ? ""
        : `
          <div class="trade-give-picker">
            <div class="trade-picker-title">Выбери карту для отдачи</div>
            <div class="trade-card-picker" id="trade-give-${trade.id}"></div>
          </div>
        `;

    return `
      ${givePicker}
      <div class="trade-actions">
        <button type="button" class="btn primary btn-trade-accept" data-id="${trade.id}">✅ Принять</button>
        <button type="button" class="btn danger btn-trade-decline" data-id="${trade.id}">✖️ Отклонить</button>
      </div>
    `;
  }

  return `
    <div class="trade-actions">
      <button type="button" class="btn danger btn-trade-cancel" data-id="${trade.id}">Отменить</button>
    </div>
  `;
}

function renderTradeLists() {
  const incomingRoot = document.getElementById("trade-incoming-list");
  const outgoingRoot = document.getElementById("trade-outgoing-list");
  const countEl = document.getElementById("trade-in-count");

  if (tradeState.incoming.length) {
    countEl.textContent = String(tradeState.incoming.length);
    countEl.classList.remove("hidden");
  } else {
    countEl.classList.add("hidden");
  }

  incomingRoot.innerHTML = tradeState.incoming.length
    ? tradeState.incoming
        .map(
          (trade) => `
            <div class="trade-offer" data-trade-id="${trade.id}">
              <div class="trade-offer-head">
                <span>От <strong>${trade.from_name}</strong></span>
              </div>
              <div class="trade-offer-cards">
                ${tradeMiniCard(trade.offered_card)}
                <div class="trade-arrow">⇄</div>
                ${tradeMiniCard(trade.requested_card)}
              </div>
              ${renderTradeOfferActions(trade)}
            </div>
          `
        )
        .join("")
    : '<p class="empty">Нет входящих предложений</p>';

  outgoingRoot.innerHTML = tradeState.outgoing.length
    ? tradeState.outgoing
        .map(
          (trade) => `
            <div class="trade-offer" data-trade-id="${trade.id}">
              <div class="trade-offer-head">
                <span>Для <strong>${trade.to_name}</strong></span>
              </div>
              <div class="trade-offer-cards">
                ${tradeMiniCard(trade.offered_card)}
                <div class="trade-arrow">→</div>
                ${tradeMiniCard(trade.requested_card)}
              </div>
              ${renderTradeOfferActions(trade)}
            </div>
          `
        )
        .join("")
    : '<p class="empty">Нет исходящих предложений</p>';

  for (const trade of tradeState.incoming) {
    if (trade.requested_card) continue;
    const picker = document.getElementById(`trade-give-${trade.id}`);
    if (!picker) continue;
    renderTradeCardPicker(picker, tradeState.myCards, {
      selectedId: tradeState.acceptGiveByTrade[trade.id] || null,
      onSelect: (id) => {
        tradeState.acceptGiveByTrade[trade.id] = id;
        renderTradeLists();
      },
      emptyText: "Нет карт",
    });
  }

  incomingRoot.querySelectorAll(".btn-trade-accept").forEach((btn) => {
    btn.addEventListener("click", () => acceptTrade(Number(btn.dataset.id)));
  });
  incomingRoot.querySelectorAll(".btn-trade-decline").forEach((btn) => {
    btn.addEventListener("click", () => declineTrade(Number(btn.dataset.id)));
  });
  outgoingRoot.querySelectorAll(".btn-trade-cancel").forEach((btn) => {
    btn.addEventListener("click", () => cancelTrade(Number(btn.dataset.id)));
  });
}

function applyTradesData(data) {
  tradeState.myCards = data.my_cards || [];
  tradeState.incoming = data.incoming || [];
  tradeState.outgoing = data.outgoing || [];
  if (data.profile) updateStats(data.profile);
  updateTradeUsernameHint();
  renderTradeCreateForm();
  renderTradeLists();
}

async function loadTrades() {
  const data = await api("/api/trades", { method: "POST" });
  applyTradesData(data);
}

async function lookupTradePartner() {
  const username = document.getElementById("trade-partner-input").value.trim();
  const label = document.getElementById("trade-partner-label");
  if (!username) {
    label.textContent = "Введи @username";
    return;
  }
  label.textContent = "Ищем…";
  try {
    const data = await api(`/api/trades/partner-cards?username=${encodeURIComponent(username)}`, {
      method: "GET",
    });
    tradeState.partnerCards = data.cards || [];
    tradeState.selectedRequestId = null;
    label.textContent = `Игрок: ${data.partner_name} · карт: ${tradeState.partnerCards.length}`;
    renderTradeCreateForm();
  } catch (err) {
    tradeState.partnerCards = [];
    tradeState.selectedRequestId = null;
    label.textContent = err.message;
    renderTradeCreateForm();
  }
}

async function createTrade() {
  const partner_username = document.getElementById("trade-partner-input").value.trim();
  if (!partner_username || !tradeState.selectedOfferId) return;

  const body = {
    partner_username,
    offered_quote_id: tradeState.selectedOfferId,
  };
  if (tradeState.selectedRequestId) {
    body.requested_quote_id = tradeState.selectedRequestId;
  }

  try {
    const data = await api("/api/trades/create", { method: "POST", body });
    applyTradesData(data);
    document.getElementById("trade-message").textContent = (data.message || "").replace(/<[^>]+>/g, "");
    tradeState.selectedOfferId = null;
    tradeState.selectedRequestId = null;
    renderTradeCreateForm();
    switchTradeTab("outgoing");
    tg?.HapticFeedback?.notificationOccurred("success");
  } catch (err) {
    showToast(err.message);
  }
}

async function acceptTrade(tradeId) {
  const trade = tradeState.incoming.find((item) => item.id === tradeId);
  const giveQuoteId = trade?.requested_card?.quote_id || tradeState.acceptGiveByTrade[tradeId];
  if (!giveQuoteId) {
    showToast("Выбери карту для отдачи");
    return;
  }

  try {
    const data = await api(`/api/trades/${tradeId}/accept`, {
      method: "POST",
      body: { give_quote_id: giveQuoteId },
    });
    applyTradesData(data);
    document.getElementById("trade-message").textContent = (data.message || "").replace(/<[^>]+>/g, "");
    delete tradeState.acceptGiveByTrade[tradeId];
    tg?.HapticFeedback?.notificationOccurred("success");
  } catch (err) {
    showToast(err.message);
  }
}

async function declineTrade(tradeId) {
  try {
    const data = await api(`/api/trades/${tradeId}/decline`, { method: "POST" });
    applyTradesData(data);
    document.getElementById("trade-message").textContent = data.message || "";
  } catch (err) {
    showToast(err.message);
  }
}

async function cancelTrade(tradeId) {
  try {
    const data = await api(`/api/trades/${tradeId}/cancel`, { method: "POST" });
    applyTradesData(data);
    document.getElementById("trade-message").textContent = data.message || "";
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
      if (name === "exchange") {
        updateDustBars(profile?.duplicate_dust || 0);
        await loadTrades();
      }
      if (name === "leaders") await loadLeaderboard();
    } catch (err) {
      showToast(err.message);
      if (name === "packs") showPackError(err.message);
    }
  });
});

document.getElementById("btn-exchange-ticket").addEventListener("click", exchangeTicket);
document.getElementById("btn-exchange-card").addEventListener("click", exchangeCard);
document.querySelectorAll(".trade-subtab").forEach((tab) => {
  tab.addEventListener("click", () => switchTradeTab(tab.dataset.tradeTab));
});
document.getElementById("btn-trade-lookup").addEventListener("click", lookupTradePartner);
document.getElementById("trade-partner-input").addEventListener("input", updateTradeCreateButton);
document.getElementById("btn-trade-create").addEventListener("click", createTrade);
document.getElementById("overlay-next").addEventListener("click", advanceReveal);
document.getElementById("overlay-close").addEventListener("click", closeReveal);

document.getElementById("reveal-stage").addEventListener("click", (e) => {
  if (e.target.closest(".btn")) return;
  if (!revealState || revealState.summaryShown) return;
  if (revealState.index < revealState.cards.length - 1) {
    revealState.index += 1;
    showRevealCard(revealState.cards[revealState.index], revealState.index, revealState.cards.length);
  } else if (revealState.packName) {
    finishReveal();
  }
});

async function boot() {
  const loader = document.getElementById("boot-loader");
  try {
    tg?.ready();
    tg?.expand();
    tg?.setHeaderColor("#0f1014");
    tg?.setBackgroundColor("#0f1014");
    refreshInitData();

    if (!initData && !tgUser) {
      showPackError("Открой Mini App через кнопку 🎮 Играть в боте");
      showToast("Нет данных Telegram");
      return;
    }

    await loadPacks();
  } catch (err) {
    showPackError(err.message);
    showToast(err.message);
  } finally {
    loader?.classList.add("hidden");
  }
}

boot();
