#!/usr/bin/env python3
"""
Verschickt eine Web-Push-Benachrichtigung an das gespeicherte iPhone-Abonnement,
sobald das Briefing generiert wurde.
"""

import os
import json
from pywebpush import webpush, WebPushException

# Diese URL muss auf deine gehostete PWA zeigen (GitHub Pages URL, siehe README)
BRIEFING_URL = os.environ.get("BRIEFING_URL", "./")


def main():
    subscription_raw = os.environ["WEB_PUSH_SUBSCRIPTION"]
    vapid_private_key = os.environ["VAPID_PRIVATE_KEY"]
    vapid_claims_email = os.environ.get("VAPID_CLAIMS_EMAIL", "mailto:example@example.com")

    subscription_info = json.loads(subscription_raw)

    with open("docs/briefing.json", "r", encoding="utf-8") as f:
        briefing = json.load(f)

    payload = {
        "title": "Dein Daily Briefing ist da",
        "body": briefing.get("summary", "Neue Weltpolitik- und Marktnachrichten warten auf dich."),
        "url": BRIEFING_URL,
    }

    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(payload),
            vapid_private_key=vapid_private_key,
            vapid_claims={"sub": vapid_claims_email},
        )
        print("Push-Benachrichtigung erfolgreich verschickt.")
    except WebPushException as ex:
        print(f"Fehler beim Verschicken der Push-Benachrichtigung: {ex}")
        raise


if __name__ == "__main__":
    main()
