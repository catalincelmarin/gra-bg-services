import json
import redis.asyncio as aioredis
import asyncio

from pydantic_core.core_schema import ValidationInfo


from pydantic import BaseModel, field_validator
from typing import Union, Dict



class Message(BaseModel):
    type: str = "json"  # Default to 'json'
    content: Union[str, Dict]  # Content can be a string (for text) or a dictionary (for JSON)
    channel: str

    @field_validator("content")
    def validate_content(cls, v, info: ValidationInfo):
        # Access the 'type' field through 'info' object
        if info.data.get("type") == "json" and not isinstance(v, dict):
            raise ValueError("For type 'json', content must be a dictionary")
        if info.data.get("type") == "text" and not isinstance(v, str):
            raise ValueError("For type 'text', content must be a string")
        return v

    @field_validator("type")
    def validate_type(cls, v):
        if v not in ("text", "json"):
            raise ValueError("Type must be 'text' or 'json'")
        return v


class Intercom:
    _instance = None
    _initialized = False

    def __new__(cls, redis_comm_url=None):
        if cls._instance is None:
            cls._instance = super(Intercom, cls).__new__(cls)
            if redis_comm_url is None:
                raise ValueError("Redis communication URL must be provided on first initialization.")
            cls._redis_comm_url = redis_comm_url
            cls._redis = aioredis.from_url(redis_comm_url)
            cls._pubsub = cls._redis.pubsub()
            cls.channels = {}
            cls._initialized = True
        return cls._instance

    async def subscribe(self, channel, callback):
        """
        Subscribe to a Redis channel asynchronously and trigger an async callback when a message is received.
        """
        await self._pubsub.subscribe(channel)

        async def listener():
            while True:
                message = await self._pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    # Call the callback and await its result
                    if type(message["data"]) is bytes:
                        data = Message(**json.loads(message["data"].decode("utf-8")))
                    else:
                        await callback(message["data"])
                        return
                    if data.type == "json":
                        data = data.content
                    else:
                        data = data.content

                    await callback(data)


        # Run the listener in the background
        task = asyncio.create_task(listener())

    async def publish(self, message: Message):
        """
        Publish a message to a Redis channel asynchronously.
        """
        redis = await aioredis.from_url(self._redis_comm_url)
        await redis.publish(message.channel, json.dumps(message.model_dump()))
        await redis.close()

    async def set(self, key, value):
        """
        Store a global variable in Redis.
        :param key: The key for the global variable
        :param value: The value to store (will be serialized as a string)
        """
        await self._redis.set(key, value)

    async def get(self, key):
        """
        Retrieve a global variable from Redis.
        :param key: The key for the global variable
        :return: The value associated with the key, or None if it does not exist
        """
        value = await self._redis.get(key)
        if value is not None:
            return value.decode('utf-8')  # Decode the bytes to string
        return None

    async def delete(self, key):
        """
        Remove a global variable from Redis.
        :param key: The key to delete
        """
        await self._redis.delete(key)

    async def exists(self, key):
        """
        Check if a key exists in Redis.
        :param key: The key to check
        :return: True if the key exists, False otherwise
        """
        return await self._redis.exists(key) > 0

    def emit(self, message: Message):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.publish(message=message))  # Non-blocking
        loop.close()
