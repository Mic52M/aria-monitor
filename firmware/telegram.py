# Telegram notifications over HTTPS.
import urequests


def send(cfg, text):
    if not cfg.TELEGRAM_ENABLED:
        return
    url = "https://api.telegram.org/bot{}/sendMessage".format(cfg.TELEGRAM_BOT_TOKEN)
    try:
        r = urequests.post(
            url,
            json={"chat_id": cfg.TELEGRAM_CHAT_ID, "text": text},
        )
        r.close()
    except Exception as e:
        print("Telegram error:", e)
