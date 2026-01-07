from typing import Any, Dict, List, Optional, Union
import datetime
from bson import ObjectId
from mongoengine.errors import DoesNotExist, NotUniqueError, ValidationError

from kimera.store.BaseRepo import BaseRepo


# -------- repo-specific exceptions (no framework binding) --------
class RepoError(Exception): ...
class RepoBadRequest(RepoError): ...
class RepoNotFound(RepoError): ...
class RepoConflict(RepoError): ...
class RepoValidationError(RepoError): ...


class AutoWireRepo(BaseRepo):
    def __init__(self, model_cls):
        super().__init__(connection_name=model_cls._meta["db_alias"])
        self.collection = self.use(model_cls._meta["collection"])
        self.model_cls = model_cls

    # ------- helpers -------
    def _oid(self, id_str: str) -> ObjectId:
        try:
            return ObjectId(id_str)
        except Exception:
            raise RepoBadRequest("Invalid ObjectId format")

    def _get_by_id(self, id_str: str):
        try:
            return self.model_cls.objects.get(id=self._oid(id_str))
        except DoesNotExist:
            raise RepoNotFound("Object does not exist")

    def _normalize(self, value: Any) -> Any:
        if isinstance(value, ObjectId):
            return str(value)
        if isinstance(value, datetime.datetime):
            return value.isoformat()
        if isinstance(value, list):
            return [self._normalize(v) for v in value]
        if isinstance(value, dict):
            return {k: self._normalize(v) for k, v in value.items()}
        return value

    # ------- CRUD -------
    def create(self, obj_data: Dict[str, Any]) -> Dict[str, Any]:
        doc = self.model_cls(**obj_data)
        try:
            doc.save()
        except NotUniqueError as err:
            raise RepoConflict(str(err))
        except ValidationError as err:
            raise RepoValidationError(str(err))
        return doc.to_dict()

    def get(self, id: str) -> Dict[str, Any]:
        doc = self._get_by_id(id)
        return doc.to_dict()

    def find(
        self,
        *,
        skip: int = 0,
        limit: Optional[int] = 50,
        order_by: Optional[Union[str, List[str]]] = None,
        **filters
    ) -> List[Dict[str, Any]]:
        qs = self.model_cls.objects(**filters)

        if order_by:
            if isinstance(order_by, str):
                order_by = [order_by]
            qs = qs.order_by(*order_by)

        if skip:
            qs = qs.skip(int(skip))

        if limit is not None:
            qs = qs.limit(int(limit))

        return [doc.to_dict() for doc in qs]

    def update(self, id: str, obj_data: Dict[str, Any]) -> Dict[str, Any]:
        doc = self._get_by_id(id)

        # assign only known fields; ignore id/_id
        fields = set(doc._fields.keys())
        for key, value in obj_data.items():
            if key in {"id", "_id"}:
                continue
            if key not in fields:
                continue
            setattr(doc, key, value)

        try:
            doc.save()
        except NotUniqueError as err:
            raise RepoConflict(str(err))
        except ValidationError as err:
            raise RepoValidationError(str(err))

        return doc.to_dict()

    def delete(self, id: str) -> bool:
        doc = self._get_by_id(id)
        doc.delete()
        return True

    # ------- Aggregation -------
    def run_aggregation(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Run a raw MongoDB aggregation pipeline against the underlying collection.
        Example:
          repo.run_aggregation([
              {"$match": {"role": "admin"}},
              {"$group": {"_id": "$role", "count": {"$sum": 1}}},
          ])
        """
        if not isinstance(pipeline, list):
            raise RepoBadRequest("Pipeline must be a list of dict stages")

        try:
            results = list(self.collection.aggregate(pipeline))
        except Exception as err:
            raise RepoBadRequest(f"AggregationError: {err}")

        return [self._normalize(doc) for doc in results]
