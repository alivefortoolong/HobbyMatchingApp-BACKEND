"""
consumer.py — RabbitMQ Worker (M3)
-----------------------------------
Run this as a separate process:
    python consumer.py

It listens on the 'activity_events' queue and creates
Notification records when like/match events arrive.

Run AFTER starting the Django server so Django is configured.
"""
import os
import sys
import django

# ── Bootstrap Django so we can use ORM outside of runserver ──
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notification_service.settings')
django.setup()

import json
import pika
from django.conf import settings
from notifications.models import Notification


def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        event = data.get('event')

        if event == 'new_like':
            Notification.objects.create(
                user_id=data['to_user'],
                from_user_id=data['from_user'],
                notif_type='like',
                message='Someone liked your profile!',
            )
            print(f"[consumer] like notif → user {data['to_user']}")

        elif event == 'new_match':
            # Notify both users
            Notification.objects.create(
                user_id=data['user1'],
                from_user_id=data['user2'],
                notif_type='match',
                message="You have a new match!",
            )
            Notification.objects.create(
                user_id=data['user2'],
                from_user_id=data['user1'],
                notif_type='match',
                message="You have a new match!",
            )
            print(f"[consumer] match notif → users {data['user1']} & {data['user2']}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"[consumer] Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def start():
    params     = pika.URLParameters(settings.RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel    = connection.channel()
    channel.queue_declare(queue='activity_events', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='activity_events', on_message_callback=callback)

    print('[consumer] Waiting for events. Press CTRL+C to stop.')
    channel.start_consuming()


if __name__ == '__main__':
    start()