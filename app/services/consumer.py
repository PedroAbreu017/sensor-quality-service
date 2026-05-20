import json
import logging
import asyncio
import aio_pika
from app.config import get_settings

logger = logging.getLogger("quality.consumer")

QUEUE_NAME = "sensor.quality.events"


async def consume_quality_events(callback):
    settings = get_settings()
    try:
        conn = await aio_pika.connect_robust(settings.rabbitmq_url)
        channel = await conn.channel()
        await channel.set_qos(prefetch_count=1)
        queue = await channel.declare_queue(QUEUE_NAME, durable=True)

        logger.info(f"[consumer] 👂 Listening on {QUEUE_NAME}")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        body = json.loads(message.body.decode())
                        await callback(body)
                    except Exception as e:
                        logger.error(f"[consumer] ✗ Error processing message: {e}")

    except Exception as e:
        logger.error(f"[consumer] ✗ Connection error: {e}")
        raise