import os
from twilio.rest import Client

def enviar_sms(destinatario: str, mensaje: str):
    try:
        sid = os.getenv("TWILIO_ACCOUNT_SID")
        token = os.getenv("TWILIO_AUTH_TOKEN")
        from_number = os.getenv("TWILIO_FROM")
        if not sid or not token or not from_number or not destinatario:
            return
        client = Client(sid, token)
        client.messages.create(
            body=mensaje,
            from_=from_number,
            to=destinatario
        )
        print(f"SMS enviado a {destinatario}")
    except Exception as e:
        print(f"Error enviando SMS: {e}")