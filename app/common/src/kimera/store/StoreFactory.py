import os

import yaml

from kimera.helpers.Helpers import Helpers
from kimera.store.ElasticStore import ElasticStore
from kimera.store.FileStore import LocalFileStore

from kimera.store.Store import Store

from pydantic import BaseModel


class MemConnection(BaseModel):
    uri: str
    namespaces: dict


class StoreNotFound(Exception):
    """Custom exception class for loading exceptions."""

    def __init__(self, message, original_exception=None):
        super().__init__(message)
        self.original_exception = original_exception

    def __str__(self):
        if self.original_exception:
            return f"{super().__str__()} (caused by: {self.original_exception})"
        return super().__str__()


class StoreFactory:
    _file_store_instances = {}
    _store_instances = {}
    _es_store_instances = {}
    _mem_store_instances = {}
    _vector_store_instances = {}
    _rdb_store_instances = {}

    @classmethod
    def get_store(cls, connection_name, uri=None, **kwargs):

        if connection_name not in cls._store_instances and uri is not None:
            cls._store_instances[connection_name] = Store(uri=uri, connection_name=connection_name, **kwargs)
        return cls._store_instances[connection_name]

    @classmethod
    def get_es_store(cls, connection_name, uri=None, index=None, **kwargs) -> ElasticStore:
        if connection_name not in cls._es_store_instances and uri is not None:
            cls._es_store_instances[connection_name] = ElasticStore(uri=uri, index=index, **kwargs)
        return cls._es_store_instances[connection_name]

    @classmethod
    def get_vector_store(cls, connection_name, collection=None, uri=None, **kwargs) -> 'VectorStore':

        from kimera.store.VectorStore import VectorStore
        if connection_name not in cls._vector_store_instances and uri is not None and collection is not None:
            v_store = Store(uri=uri, connection_name=connection_name, **kwargs)
            cls._vector_store_instances[connection_name] = VectorStore(store=v_store, collection_name=collection, **kwargs)
        elif (connection_name in cls._vector_store_instances and
              connection_name + "_" + collection not in cls._vector_store_instances and uri is None and collection is not None):
            v_store = cls._vector_store_instances[connection_name].repo.use_store
            cls._vector_store_instances[connection_name + "_" + collection] = VectorStore(
                store=v_store,
                collection_name=collection,
                **kwargs
            )
            return cls._vector_store_instances[connection_name + "_" + collection]
        elif collection is not None and connection_name + "_" + collection in cls._vector_store_instances:
            return cls._vector_store_instances[connection_name + "_" + collection]

        return cls._vector_store_instances[connection_name]

    @classmethod
    def get_mem_store(cls, namespace="_root", connection_name="default", uri=None, **kwargs) -> 'MemStore':
        from kimera.store.MemStore import MemStore
        """Get or create a Redis memory store instance by namespace."""
        if connection_name not in cls._mem_store_instances and uri is not None:
            cls._mem_store_instances[connection_name] = MemConnection(uri=uri, namespaces=dict())

        if namespace not in cls._mem_store_instances[connection_name].namespaces.keys():
            conn = cls._mem_store_instances[connection_name]
            cls._mem_store_instances[connection_name].namespaces[namespace] = MemStore(
                uri=conn.uri,
                connection_name=connection_name,
                namespace=namespace,
                **kwargs
            )
        if (connection_name in cls._mem_store_instances and
                namespace in cls._mem_store_instances[connection_name].namespaces.keys()):

            return cls._mem_store_instances[connection_name].namespaces.get(namespace)
        else:
            raise StoreNotFound(f" {connection_name}:{namespace} does not exit or requires uri")

    @classmethod
    def get_fstore(cls, store_name, path=None, **kwargs) -> LocalFileStore:
        if store_name not in cls._file_store_instances and path is not None:
            cls._file_store_instances[store_name] = LocalFileStore(path=path, **kwargs)
        return cls._file_store_instances[store_name]


    @classmethod
    def get_rdb_store(cls, connection_name, uri=None, **kwargs):
        from kimera.db.Database import Database
        if connection_name not in cls._rdb_store_instances and uri is not None:
            cls._rdb_store_instances[connection_name] = Database(uri=uri, connection_name=connection_name, **kwargs)
        return cls._rdb_store_instances[connection_name]



    @staticmethod
    def load_stores(stores_path: str, verbose: bool = False):
        pth = f"{stores_path}/app"
        total = 0
        loaded = 0
        failed = 0

        for root, dirs, files in os.walk(pth):
            for filename in files:
                if filename.startswith("stores.") and filename.endswith(".yaml"):
                    file_path = os.path.join(root, filename)

                    if os.path.isfile(file_path):
                        with open(file_path, "r") as file:
                            file_content = yaml.safe_load(file) or {}
                            more_stores = file_content.get("stores", [])

                            for store in more_stores:
                                total += 1
                                store_type = store.get("type")
                                uri = os.getenv(store.get("uri", 'NO_STORE'))
                                kwargs = store.get("kwargs", {}) or {}

                                try:
                                    if store_type == "sql":
                                        StoreFactory.get_rdb_store(
                                            connection_name=store["name"],
                                            uri=uri,
                                            **kwargs
                                        )
                                    elif store_type == "nosql":
                                        StoreFactory.get_store(
                                            connection_name=store["name"],
                                            uri=uri,
                                            **kwargs
                                        )
                                    elif store_type == "elastic":
                                        StoreFactory.get_es_store(
                                            connection_name=store["name"],
                                            uri=uri,
                                            index=store.get("index"),
                                            **kwargs
                                        )
                                    elif store_type == "mem":
                                        StoreFactory.get_mem_store(
                                            connection_name=store["name"],
                                            uri=uri,
                                            **kwargs
                                        )
                                    elif store_type == "vector":
                                        StoreFactory.get_vector_store(
                                            connection_name=store["name"],
                                            uri=uri,
                                            collection=store["collection"],
                                            **kwargs
                                        )
                                    elif store_type == "files":
                                        StoreFactory.get_fstore(
                                            store_name=store["name"],
                                            path=store["path"],
                                            **kwargs
                                        )
                                    loaded += 1
                                except Exception as e:
                                    failed += 1
                                    Helpers.tracePrint(e, message=f"Failed to load store: {store}")

        if verbose:
            Helpers.sysPrint(f"STORES {total}", f"loaded {loaded} | failed {failed}")
