import os
import base64
import pickle
from typing import Dict, List, Any

import redis
from kimera.helpers.Helpers import Helpers
import binascii

debug = os.getenv("DEBUG_STORES",False)

class MemStore:
    def __init__(self, uri=None, connection_name='default', namespace='_root', **kwargs):
        self.uri = uri
        self.connection_name = connection_name
        self.namespace = namespace
        self.client = redis.Redis.from_url(self.uri) if self.uri else None

    def _full_key(self, key: str) -> str:
        return f"{self.namespace}:{key}"

    def set(self, key: str, value: Any):
        """Pickle and base64-encode any value and store in Redis."""
        namespaced_key = self._full_key(key)
        try:
            pickled = pickle.dumps(value)
            encoded = base64.b64encode(pickled).decode("ascii")
            self.client.set(namespaced_key, encoded)
            if debug:
                Helpers.sysPrint(f"Set key:", namespaced_key)
        except Exception as e:
            Helpers.errPrint(f"Failed to set key {namespaced_key}: {e}", os.path.basename(__file__))

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve and decode a value from Redis."""
        namespaced_key = self._full_key(key)
        try:
            if not self.client.exists(namespaced_key):
                return default

            raw = self.client.get(namespaced_key)
            if raw is None:
                return default

            decoded = base64.b64decode(raw, validate=True)
            value = pickle.loads(decoded)
            return value
        except (binascii.Error, pickle.UnpicklingError, Exception) as e:
            Helpers.errPrint(f"Failed to get key {namespaced_key}: {e}", os.path.basename(__file__))
            return default

    def delete(self, key: str):
        """Delete a key from Redis."""
        namespaced_key = self._full_key(key)
        try:
            self.client.delete(namespaced_key)
            if debug:
                Helpers.print(f"Deleted key {namespaced_key} from Redis.")
        except Exception as e:
            Helpers.errPrint(f"Failed to delete key {namespaced_key}: {e}", os.path.basename(__file__))

    def keys(self, pattern='*') -> List[str]:
        """List all keys matching the pattern within the namespace."""
        try:
            full_pattern = f"{self.namespace}:{pattern}"
            keys = self.client.keys(full_pattern)
            return [key.decode('utf-8') for key in keys]
        except Exception as e:
            Helpers.errPrint(f"Failed to retrieve keys: {e}", os.path.basename(__file__))
            return []

    def flush(self):
        """Delete all keys within the namespace."""
        try:
            keys = self.keys()
            if keys:
                self.client.delete(*keys)
                if debug:
                    Helpers.print(f"Flushed {len(keys)} keys from namespace {self.namespace}.")
            else:
                if debug:
                    Helpers.print(f"No keys found in namespace {self.namespace} to flush.")
        except Exception as e:
            Helpers.errPrint(f"Failed to flush namespace {self.namespace}: {e}", os.path.basename(__file__))

    def close(self):
        """Close the Redis connection."""
        if self.client:
            self.client.close()
            Helpers.print("Disconnected from Redis.")

    # === HASH METHODS for HIGH-FREQUENCY ACCESS ===

    def hset(self, key: str, field: str = None, value: Any = None, mapping: Dict[str, Any] = None):
        """
        Set one or many fields in a Redis hash.
        Provide either a single (field + value) or a full mapping.
        """
        try:
            redis_key = self._full_key(key)
            if mapping:
                self.client.hset(redis_key, mapping=mapping)
            elif field is not None:
                self.client.hset(redis_key, field, value)
            if debug:
                Helpers.sysPrint(f"HSET key: {redis_key}")
        except Exception as e:
            Helpers.errPrint(f"Failed to HSET {key}: {e}", os.path.basename(__file__))

    def hget(self, key: str, field: str) -> Any:
        """
        Get a single field from a Redis hash.
        Returns string or None.
        """
        try:
            redis_key = self._full_key(key)
            result = self.client.hget(redis_key, field)
            return result.decode("utf-8") if result is not None else None
        except Exception as e:
            Helpers.errPrint(f"Failed to HGET {key}:{field}: {e}", os.path.basename(__file__))
            return None

    def hgetall(self, key: str) -> Dict[str, Any]:
        """
        Get all fields and values from a Redis hash.
        Returns a dict of strings.
        """
        try:
            redis_key = self._full_key(key)
            raw = self.client.hgetall(redis_key)
            return {k.decode("utf-8"): v.decode("utf-8") for k, v in raw.items()}
        except Exception as e:
            Helpers.errPrint(f"Failed to HGETALL {key}: {e}", os.path.basename(__file__))
            return {}

    def hdel(self, key: str, field: str):
        """
        Delete a field from a Redis hash.
        """
        try:
            redis_key = self._full_key(key)
            self.client.hdel(redis_key, field)
            if debug:
                Helpers.print(f"HDEL field '{field}' from {redis_key}")
        except Exception as e:
            Helpers.errPrint(f"Failed to HDEL {key}:{field}: {e}", os.path.basename(__file__))
