# Daily Briefing

Eine kleine PWA (Progressive Web App), die dir jeden Morgen automatisch einen
KI-generierten Bericht zu Weltpolitik & Märkten erstellt und dich per
Push-Benachrichtigung aufs iPhone informiert — komplett kostenlos gehostet,
nur die Anthropic-API-Nutzung kostet ein paar Cent pro Tag.

## Wie es funktioniert

1. Jeden Morgen startet ein **GitHub Actions Cron-Job** (läuft in der Cloud,
   dein Handy/Mac muss nicht an sein)
2. Das Skript fragt **Claude mit Websuche** nach den wichtigsten Nachrichten
3. Das Ergebnis wird als `docs/briefing.json` gespeichert und automatisch
   auf **GitHub Pages** veröffentlicht (deine PWA)
4. Eine **Web-Push-Benachrichtigung** geht an dein iPhone
5. Tippst du drauf, öffnet sich die App mit dem fertigen Bericht

## Einmaliges Setup

### 1. Repo befüllen

Lade alle Dateien aus diesem Projekt in dein leeres GitHub-Repo (per
`git push` oder Drag & Drop im GitHub-Web-UI unter "Add file" → "Upload files").

### 2. GitHub Pages aktivieren

- Im Repo: **Settings → Pages**
- Unter "Build and deployment" → Source: **"Deploy from a branch"**
- Branch: `main`, Ordner: **`/docs`** → Save
- Nach 1-2 Minuten ist deine App erreichbar unter:
  `https://<dein-username>.github.io/daily-briefing/`

### 3. GitHub Secrets eintragen

Im Repo: **Settings → Secrets and variables → Actions → New repository secret**

Trage folgende Secrets ein:

| Name | Wert |
|---|---|
| `ANTHROPIC_API_KEY` | dein Key von console.anthropic.com |
| `VAPID_PRIVATE_KEY` | wurde dir im Chat gegeben (nicht hier im Repo speichern!) |
| `VAPID_CLAIMS_EMAIL` | z.B. `mailto:deine@email.de` |
| `WEB_PUSH_SUBSCRIPTION` | trägst du in Schritt 5 ein (nach dem ersten App-Öffnen) |

Zusätzlich unter **Settings → Secrets and variables → Actions → Variables**:

| Name | Wert |
|---|---|
| `BRIEFING_URL` | `https://<dein-username>.github.io/daily-briefing/` |

### 4. App auf dein iPhone legen

- Öffne `https://<dein-username>.github.io/daily-briefing/` in **Safari**
  (muss Safari sein, nicht Chrome — nur Safari unterstützt PWA-Push auf iOS)
- Teilen-Symbol → **"Zum Home-Bildschirm"**
- Öffne die App danach **vom Home-Bildschirm aus** (nicht mehr im Browser) —
  das ist wichtig, sonst funktioniert Push auf iOS nicht zuverlässig

### 5. Benachrichtigungen aktivieren & Subscription eintragen

- In der App: Button **"Benachrichtigungen aktivieren"** antippen, erlauben
- Ein Textfeld erscheint mit einem JSON-Block — das ist deine persönliche
  "Adresse", an die Push-Nachrichten geschickt werden
- Kopier den kompletten Inhalt (Button "Kopieren")
- Trag ihn als GitHub Secret `WEB_PUSH_SUBSCRIPTION` ein (siehe Schritt 3)

### 6. Ersten Testlauf starten

- Im Repo: **Actions → Daily Briefing → Run workflow** (manueller Trigger)
- Nach ein paar Minuten solltest du eine Push-Benachrichtigung bekommen
- Tippst du drauf, öffnet sich die App mit dem fertigen Bericht

## Laufender Betrieb

- Der Cron-Job läuft automatisch **täglich um 7:00 UTC** (9:00 Uhr MESZ /
  8:00 Uhr MEZ im Winter) — anpassbar in
  `.github/workflows/daily-briefing.yml`
- Kosten: nur die Anthropic-API-Nutzung, GitHub Actions/Pages sind kostenlos
- **Stoppen:** Actions-Tab → Workflow deaktivieren, oder Secrets löschen

## Troubleshooting

- **Keine Push-Nachricht angekommen:** Prüfe im Actions-Tab, ob der Lauf
  grün war. Bei Fehler im "Send push notification"-Schritt: Subscription ist
  evtl. abgelaufen (iOS erneuert sie gelegentlich) — Schritt 5 wiederholen.
- **App zeigt nur Platzhalter:** Der erste echte Lauf ist noch nicht
  durchgelaufen — manuell auslösen (Schritt 6).
- **"Benachrichtigungen aktivieren" tut nichts:** Läuft die App wirklich vom
  Home-Bildschirm (nicht im Safari-Tab)? Das ist auf iOS zwingend nötig.
