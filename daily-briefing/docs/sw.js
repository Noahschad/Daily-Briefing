// Service Worker für Push-Benachrichtigungen und Offline-Fähigkeit

const CACHE_NAME = "briefing-cache-v1";

self.addEventListener("install", (event) => {
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim());
});

// Eingehende Push-Nachricht -> Benachrichtigung anzeigen
self.addEventListener("push", (event) => {
  let data = { title: "Daily Briefing", body: "Dein neuer Bericht ist da.", url: "./" };
  try {
    data = event.data.json();
  } catch (e) {
    // Fallback falls kein JSON gesendet wurde
  }

  const options = {
    body: data.body,
    icon: "icon-192.png",
    badge: "icon-192.png",
    data: { url: data.url || "./" },
    tag: "daily-briefing",
    renotify: true,
  };

  event.waitUntil(self.registration.showNotification(data.title, options));
});

// Klick auf die Benachrichtigung -> App öffnen
self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const targetUrl = event.notification.data?.url || "./";

  event.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if (client.url.includes(self.registration.scope) && "focus" in client) {
          client.navigate(targetUrl);
          return client.focus();
        }
      }
      if (clients.openWindow) {
        return clients.openWindow(targetUrl);
      }
    })
  );
});
