from abc import abstractmethod
from typing import Any, List

from pymongo.collection import Collection

from kimera.store.StoreFactory import StoreFactory


class BaseRepo:
    def __init__(self, connection_name="_root"):
        self.use_store = StoreFactory.get_store(connection_name=connection_name)

    def connect(self, db):
        if self.use_store is not None:
            self.use_store.connect(db)

    def use(self, collection) -> Collection:
        if self.use_store is not None:
            return self.use_store.use(collection)

    @abstractmethod
    def create(self, obj_data: dict[str, Any]) -> dict[str, Any]:
        """Insert a new record and return the created object as a dict."""
        raise NotImplementedError

    @abstractmethod
    def get(self, id: Any) -> dict[str, Any]:
        """Retrieve a record by its primary identifier."""
        raise NotImplementedError

    @abstractmethod
    def find(self, **filters: Any) -> List[dict[str, Any]]:
        """Return all records matching the given filters."""
        raise NotImplementedError

    @abstractmethod
    def update(self, id: Any, obj_data: dict[str, Any]) -> dict[str, Any]:
        """Update a record by id and return the updated object."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, id: Any) -> bool:
        """Delete a record by id and return True if deleted."""
        raise NotImplementedError
