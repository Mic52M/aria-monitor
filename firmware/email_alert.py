# Email alerts through the Resend API (HTTPS). No extra library: uses urequests.
import urequests


def send(cfg, subject, text):
    if not getattr(cfg, "EMAIL_ENABLED", False):
        return
    try:
        r = urequests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": "Bearer " + cfg.RESEND_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "from": cfg.EMAIL_FROM,
                "to": [cfg.EMAIL_TO],
                "subject": subject,
                "text": text,
            },
        )
        print("email:", r.status_code)
        r.close()
    except Exception as e:
        print("email error:", e)
