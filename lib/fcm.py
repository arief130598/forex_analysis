from firebase_admin import messaging


def send_notif(topic, title, body):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        topic=topic,
    )
    messaging.send(message)
