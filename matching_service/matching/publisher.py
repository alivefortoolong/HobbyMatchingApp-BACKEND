"""
publisher.py
------------
Publishes events to RabbitMQ so notification_service can consume them.
Uses a simple fire-and-forget approach with a persistent queue.

Events published:
  - new_like  : when user A likes user B
  - new_match : when a mutual like creates a match
"""
import json
import pika
from django.conf import settings


def _get_channel():
    params     = pika.URLParameters(settings.RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel    = connection.channel()
    channel.queue_declare(queue='activity_events', durable=True)
    return connection, channel


def publish_like(from_user_id: int, to_user_id: int):
    _publish({
        'event':     'new_like',
        'from_user': from_user_id,
        'to_user':   to_user_id,
    })


def publish_match(user1_id: int, user2_id: int):
    _publish({
        'event': 'new_match',
        'user1': user1_id,
        'user2': user2_id,
    })


def _publish(data: dict):
    try:
        connection, channel = _get_channel()
        channel.basic_publish(
            exchange='',
            routing_key='activity_events',
            body=json.dumps(data),
            properties=pika.BasicProperties(delivery_mode=2),  # persistent
        )
        connection.close()
    except Exception as e:
        # RabbitMQ not running locally during dev — just log and continue
        print(f"[RabbitMQ] Could not publish event: {e}")