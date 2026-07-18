#!/usr/bin/env python3
"""
Generiert das tägliche Briefing (Weltpolitik + Märkte) über die Anthropic API
mit Websuche, und speichert das Ergebnis als HTML in docs/briefing.html
sowie als JSON in docs/briefing.json (für die PWA).
"""

import os
import json
import datetime
from anthropic import Anthropic

# --- Konfiguration ---
MODEL = "claude-sonnet-4-6"  # gutes Preis-/Qualitätsverhältnis für diesen Zweck
MAX_TOKENS = 8000  # genug Spielraum für Websuche + langen Bericht

PROMPT = """Erstelle ein hochwertiges Daily Briefing mit den wichtigsten weltpolitischen und wirtschaftlichen Nachrichten der letzten 24 Stunden. Zielgruppe: informierter Leser, will schnell aber fundiert auf dem neuesten Stand sein. Lesezeit: 10-15 Minuten.

STRUKTUR:

1. DAS WICHTIGSTE IN KÜRZE
3-4 Sätze Überblick über die wichtigsten Entwicklungen.

2. WELTPOLITIK (nach Relevanz sortiert, nicht nach Region)
Decke ab, aber nur was wirklich relevant ist:
- USA & transatlantische Beziehungen
- Europa & EU-Politik
- China & Asien-Pazifik
- Globale Konflikte & Sicherheitspolitik
Pro Meldung: prägnante Überschrift, 3-5 Sätze Fakten + Einordnung, Quellenangabe.

3. MÄRKTE & WIRTSCHAFT
- Kurzüberblick große Indizes (DAX, S&P 500, Nasdaq, Dow, ggf. Nikkei/Hang Seng) mit Bewegung
- Relevante Branchenentwicklungen (Tech, Energie, Finanzen, Auto)
- Alles extrem Marktrelevante (Zinsentscheidungen, große Unternehmensmeldungen, geopolitische Marktschocks)

QUALITÄTSANFORDERUNGEN:
- Nutze ausschließlich seriöse Quellen (Reuters, Bloomberg, FT, AP, Handelsblatt, dpa)
- Bei widersprüchlichen Infos: kennzeichnen
- Keine reine Linkliste – echte Zusammenfassungen mit Einordnung
- Lieber 8-10 wichtige Meldungen gut erklärt als 20 oberflächliche

Antworte NUR mit validem JSON in exakt diesem Format, keine Markdown-Codeblöcke, kein Text davor/danach:
{
  "date": "YYYY-MM-DD",
  "summary": "3-4 Sätze Überblick",
  "politics": [
    {"headline": "...", "body": "...", "source": "..."}
  ],
  "markets": [
    {"headline": "...", "body": "...", "source": "..."}
  ]
}
"""


def generate_briefing() -> dict:
    client = Anthropic()  # liest ANTHROPIC_API_KEY aus der Umgebung

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": PROMPT}],
    )

    # Den finalen Text-Block extrahieren (nach eventuellen Tool-Aufrufen)
    text_blocks = [b.text for b in response.content if b.type == "text"]
    raw_text = "\n".join(text_blocks).strip()

    # Fallback: falls doch mal Codeblock-Fences drin sind
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    if not raw_text:
        # Diagnose-Infos ins Log schreiben, damit man im Actions-Log sieht, was los war
        print(f"WARNUNG: Leere Textantwort. stop_reason={response.stop_reason}")
        print(f"Anzahl content blocks: {len(response.content)}")
        for i, b in enumerate(response.content):
            print(f"  Block {i}: type={b.type}")
        raise RuntimeError(
            f"Claude hat keinen Text zurückgegeben (stop_reason={response.stop_reason}). "
            "Möglicherweise max_tokens erreicht, bevor der Bericht fertig war."
        )

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        print(f"WARNUNG: JSON-Parsing fehlgeschlagen: {e}")
        print(f"Erhaltener Text (erste 2000 Zeichen):\n{raw_text[:2000]}")
        raise

    return data


def main():
    today = datetime.date.today().isoformat()
    data = generate_briefing()
    data.setdefault("date", today)

    os.makedirs("docs", exist_ok=True)

    with open("docs/briefing.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Briefing für {data['date']} erfolgreich generiert.")


if __name__ == "__main__":
    main()
