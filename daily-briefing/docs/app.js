// ACHTUNG: Diesen Wert nach dem Generieren deiner VAPID-Keys ersetzen
// (siehe README, Schritt "VAPID-Keys generieren")
const VAPID_PUBLIC_KEY = "BMZZI5y-pBY508tbXgGjAMgVOgwKDt9JRHCzGgfwEvcBnKvwSUtUY9-M1bQ0hkjdSUp_knOC72GelbYTBtMXhfo";

function urlBase64ToUint8Array(base64String) {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
  const rawData = window.atob(base64);
  return Uint8Array.from([...rawData].map((c) => c.charCodeAt(0)));
}

async function registerServiceWorker() {
  if (!("serviceWorker" in navigator)) {
    console.warn("Service Worker wird nicht unterstützt.");
    return null;
  }
  return navigator.serviceWorker.register("sw.js");
}

async function subscribeToPush() {
  const status = document.getElementById("push-status");
  try {
    const permission = await Notification.requestPermission();
    if (permission !== "granted") {
      status.textContent = "Benachrichtigungen wurden nicht erlaubt.";
      return;
    }

    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
    });

    const subJson = JSON.stringify(subscription, null, 2);
    document.getElementById("subscription-output").value = subJson;
    document.getElementById("subscription-box").style.display = "block";
    status.textContent = "Aktiviert! Kopiere jetzt das Feld unten in dein GitHub Secret.";
  } catch (err) {
    status.textContent = "Fehler: " + err.message;
    console.error(err);
  }
}

function copySubscription() {
  const el = document.getElementById("subscription-output");
  el.select();
  document.execCommand("copy");
  document.getElementById("copy-btn").textContent = "Kopiert!";
}

async function loadBriefing() {
  const container = document.getElementById("briefing");
  try {
    const res = await fetch("briefing.json?t=" + Date.now());
    if (!res.ok) throw new Error("Noch kein Briefing vorhanden.");
    const data = await res.json();
    renderBriefing(data, container);
  } catch (e) {
    container.innerHTML = `<p class="empty">Noch kein Briefing vorhanden. Der erste Lauf kommt morgen früh, oder löse ihn manuell in GitHub Actions aus.</p>`;
  }
}

function renderBriefing(data, container) {
  const section = (title, items) =>
    items && items.length
      ? `<h2>${title}</h2>` +
        items
          .map(
            (i) => `
        <article class="item">
          <h3>${escapeHtml(i.headline)}</h3>
          <p>${escapeHtml(i.body)}</p>
          <span class="source">${escapeHtml(i.source || "")}</span>
        </article>`
          )
          .join("")
      : "";

  container.innerHTML = `
    <div class="date">${escapeHtml(data.date)}</div>
    <p class="summary">${escapeHtml(data.summary)}</p>
    ${section("Weltpolitik", data.politics)}
    ${section("Märkte & Wirtschaft", data.markets)}
  `;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

window.addEventListener("load", () => {
  registerServiceWorker();
  loadBriefing();
  document.getElementById("enable-btn").addEventListener("click", subscribeToPush);
  document.getElementById("copy-btn").addEventListener("click", copySubscription);
});
