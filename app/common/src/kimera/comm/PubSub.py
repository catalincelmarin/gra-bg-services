import json
from collections.abc import Callable
from enum import Enum
import asyncio
from typing import Awaitable, Any
import threading

from confluent_kafka import Consumer, Producer, KafkaException
from confluent_kafka.admin import AdminClient, NewTopic
from kimera.helpers.Helpers import Helpers
from kimera.helpers.DataMapper import DataMapper


class KafkaContentTypes(Enum):
    APPLICATION_JSON = "application/json"
    TEXT_PLAIN = "text/plain"



class Pub:
    def __init__(self, kafka_servers, topic, contentType: KafkaContentTypes = KafkaContentTypes.APPLICATION_JSON, ack_handler: Callable[[dict], Awaitable[None]] | None = None):
        self.topic = topic
        self.bootstrap_servers = kafka_servers
        self.contentType = contentType.value
        self._ack_handler = ack_handler
        self._ack_loop = None
        self._ack_loop_thread = None
        producer_config = {'bootstrap.servers': self.bootstrap_servers}

        try:
            self.producer = Producer(producer_config)
        except Exception as e:
            raise KafkaException(f"Failed to create Kafka Producer: {e}")

    def _ensure_ack_loop(self):
        if self._ack_loop is None:
            loop = asyncio.new_event_loop()
            self._ack_loop = loop
            t = threading.Thread(target=self._run_loop, args=(loop,), daemon=True)
            self._ack_loop_thread = t
            t.start()

    @staticmethod
    def _run_loop(loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def _build_ack_event(self, err, msg):
        headers_list = msg.headers() or []
        try:
            headers = dict(headers_list)
        except Exception:
            headers = {}
        try:
            ct = headers.get('Content-Type', self.contentType)
            if isinstance(ct, bytes):
                ct = ct.decode('utf-8')
        except Exception:
            ct = self.contentType

        raw_value = None
        try:
            raw_value = msg.value()
        except Exception:
            raw_value = None

        data = None
        if raw_value is not None:
            try:
                text = raw_value.decode('utf-8')
            except Exception:
                text = None
            if ct == KafkaContentTypes.APPLICATION_JSON.value and text is not None:
                try:
                    data = json.loads(text)
                except Exception as ex:
                    data = {"text": text}
            else:
                data = {"text": text} if text is not None else None

        meta = {
            "topic": msg.topic() if hasattr(msg, 'topic') else self.topic,
            "partition": msg.partition() if hasattr(msg, 'partition') else None,
            "offset": msg.offset() if hasattr(msg, 'offset') else None,
            "timestamp": msg.timestamp()[1] if hasattr(msg, 'timestamp') and msg.timestamp() else None,
            "key": msg.key().decode('utf-8') if hasattr(msg, 'key') and msg.key() else None,
            "headers": {k: (v.decode('utf-8') if isinstance(v, bytes) else v) for k, v in (headers.items() if isinstance(headers, dict) else [])},
            "contentType": ct,
        }

        if err is None:
            return {"status": "ok", "error": None, "meta": meta, "data": data}
        else:
            err_msg = str(err)
            code = getattr(err, 'code', None)
            return {"status": "error", "error": {"message": err_msg, "code": str(code) if code is not None else None}, "meta": meta, "data": data}

    def _delivery_callback(self, err, msg, user_callback=None):
        if user_callback is not None:
            try:
                user_callback(err, msg)
            except Exception:
                pass
        if self._ack_handler is not None:
            try:
                self._ensure_ack_loop()
                event = self._build_ack_event(err, msg)
                asyncio.run_coroutine_threadsafe(self._ack_handler(event), self._ack_loop)
            except Exception:
                pass

    def topicExists(self):
        try:
            admin_client = AdminClient({'bootstrap.servers': self.bootstrap_servers})
            topic_metadata = admin_client.list_topics(timeout=5)
            return self.topic in topic_metadata.topics
        except Exception as e:
            raise KafkaException(f"Error checking topic existence: {e}")

    def _create_topic_if_not_exists(self):
        if not self.topicExists():
            try:
                admin_client = AdminClient({'bootstrap.servers': self.bootstrap_servers})
                new_topic = NewTopic(self.topic, num_partitions=1, replication_factor=1)
                admin_client.create_topics([new_topic])
            except Exception as e:
                raise KafkaException(f"Failed to create topic {self.topic}: {e}")

    def publish(self, message=None, callback=None):
        self._create_topic_if_not_exists()
        try:
            message = DataMapper.json({"data": message})
            headers = [('Content-Type', self.contentType)]

            if callback is not None or self._ack_handler is not None:
                self.producer.produce(self.topic, value=message.encode('utf-8'), headers=headers, callback=lambda err, msg: self._delivery_callback(err, msg, callback))
            else:
                self.producer.produce(self.topic, value=message.encode('utf-8'), headers=headers)
        except Exception as e:
            raise KafkaException(f"Failed to publish message: {e}")
        finally:
            self.producer.flush()
            if callback is not None:
                self.producer.poll(0)


class Sub:
    def __init__(self, kafka_servers, group_id, topic, name,handler:Callable[..., Awaitable[Any]], contentType=KafkaContentTypes.APPLICATION_JSON):
        Helpers.sysPrint("INIT:", topic)
        self.group_id = group_id
        self.topic = topic
        self.name = name
        self.handler = handler
        self.bootstrap_servers = kafka_servers
        self.contentType = contentType if contentType in [KafkaContentTypes.TEXT_PLAIN, KafkaContentTypes.APPLICATION_JSON] else KafkaContentTypes.APPLICATION_JSON

        consumer_config = {
            'bootstrap.servers': self.bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        }

        try:
            self.consumer = Consumer(consumer_config)
        except Exception as e:
            raise KafkaException(f"Failed to create Kafka Consumer: {e}")

    def topicExists(self):
        try:
            admin_client = AdminClient({'bootstrap.servers': self.bootstrap_servers})
            topic_metadata = admin_client.list_topics(timeout=5)
            return self.topic in topic_metadata.topics
        except Exception as e:
            raise KafkaException(f"Error checking topic existence: {e}")

    async def _run(self):
        handler = self.handler
        Helpers.sysPrint("LISTEN:", self.topic)
        while not self.topicExists():
            Helpers.sysPrint("TOPIC", f"{self.topic} is unavailable")
            await asyncio.sleep(300)

        self.consumer.subscribe([self.topic])

        try:
            while True:
                message = self.consumer.poll(1.0)
                if message is None:
                    continue
                if message.error():
                    raise KafkaException(f"Consumer error: {message.error()}")
                Helpers.print(message.headers())
                Helpers.print(message.value())
                if message.value():
                    msg = message.value().decode("utf-8")
                    contentType = self.contentType.value

                    Helpers.print(message.headers())
                    if message.headers() is None:
                        raise KafkaException(f"Missing headers: {msg}")
                    else:
                        try:
                            headers = dict(message.headers())
                        except Exception as e:
                            headers = {"Content-Type": b"text/plain"}

                        contentType = contentType if 'Content-Type' not in headers \
                            else headers['Content-Type'].decode("utf-8")

                    if contentType != self.contentType.value:
                        raise KafkaException(f"Wrong content type: {contentType}")

                    if self.contentType == KafkaContentTypes.APPLICATION_JSON and contentType == self.contentType.value:
                        msg = json.loads(msg)

                    if handler is not None and message is not None:
                        await asyncio.gather(handler(data=msg))

        finally:
            self.consumer.close()

    def listen(self,*args,**kwargs):
        Helpers.sysPrint(f"CONSUMER {self.name}", f"ON g: {self.group_id} t:{self.topic}")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self._run())
        except KeyboardInterrupt:
            print("Keyboard interrupt detected. Stopping the event loop...")
        except Exception as e:
            raise KafkaException(f"Unexpected error in consumer: {e}")
        finally:
            loop.close()

class PubFactory:
    _instances = {}


    @classmethod
    def set(cls,kafka_servers, name, topic, contentType: KafkaContentTypes = KafkaContentTypes.APPLICATION_JSON, ack_handler: Callable[[dict], Awaitable[None]] | None = None):
        if name not in cls._instances:
            cls._instances[name] = Pub(kafka_servers=kafka_servers, topic=topic,
                                             contentType=contentType, ack_handler=ack_handler)

    @classmethod
    def get(cls, name) -> Pub:
        if name not in cls._instances:
            raise KafkaException(f"Publisher instance '{name}' not found.")
        return cls._instances[name]

    @classmethod
    def all(cls):
        return cls._instances

    @staticmethod
    def publish(to, message):
        pub_instance = PubFactory.get(to)
        if not pub_instance:
            raise KafkaException(f"No publisher instance found for '{to}'.")
        pub_instance.publish(message=message)
