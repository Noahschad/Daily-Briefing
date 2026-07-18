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
from json_repair import repair_json

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
- WICHTIG für gültiges JSON: Verwende IN DEN TEXTEN NIEMALS normale doppelte Anführungszeichen ("). Falls du ein Zitat oder einen Begriff hervorheben willst, nutze stattdessen einfache Anführungszeichen (') oder deutsche Anführungszeichen (» «).

Antworte NUR mit validem JSON in exakt diesem Format. Deine Antwort MUSS mit dem Zeichen { beginnen und mit } enden – keine Einleitung, kein "Hier ist...", keine Markdown-Formatierung, keine Codeblock-Fences, kein Text davor oder danach:
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
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 6}],
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

    # Robuste Extraktion: nimm alles zwischen der ersten "{" und der letzten "}",
    # falls Claude trotz Anweisung noch einleitenden Text davor/danach gesetzt hat
    first_brace = raw_text.find("{")
    last_brace = raw_text.rfind("}")
    if first_brace == -1 or last_brace == -1 or last_brace < first_brace:
        print(f"WARNUNG: Kein JSON-Objekt gefunden im Text (erste 2000 Zeichen):\n{raw_text[:2000]}")
        raise RuntimeError("Kein JSON-Objekt in der Antwort gefunden.")

    json_str = raw_text[first_brace : last_brace + 1]

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"WARNUNG: JSON-Parsing fehlgeschlagen, versuche Reparatur: {e}")
        try:
            repaired = repair_json(json_str)
            data = json.loads(repaired)
            print("JSON erfolgreich repariert.")
        except Exception as repair_error:
            print(f"WARNUNG: Auch Reparatur fehlgeschlagen: {repair_error}")
            print(f"Extrahierter String (erste 2000 Zeichen):\n{json_str[:2000]}")
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
