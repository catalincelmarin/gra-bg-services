from __future__ import annotations
from typing import Any, Optional, Sequence


from kimera.store.StoreFactory import StoreFactory


class AutoWireRepo:
    """
    Async Base Repository for SQLAlchemy ORM models autoloaded from db._Base.classes.
    The DB store comes from StoreFactory. You MUST call `await repo.connect()` before CRUD.

    Subclasses must set:
      - model_name: the key under db._Base.classes (e.g., "operators")
      - store_name: optional; defaults to "default"
    """

    model_name: str = None        # set in subclass, e.g., "operators"
    store_name: str = "default"   # override if needed

    def __init__(self):
        if not self.model_name:
            raise TypeError("Subclasses must set `model_name` to the mapped SQLAlchemy class name.")
        self.store_name = getattr(self, "store_name", "default")
        self.db = StoreFactory.get_rdb_store(self.store_name)
        self.model = None  # resolved in connect()

    def get_class(self, table_name: str):
        for name in dir(self.db._Base.classes):
            if name.lower() == table_name.lower():
                return getattr(self.db._Base.classes, name)
        raise AttributeError(f"Table {table_name} not found in automap.")

    async def connect(self):
        """Connects the DB and resolves the model from automap."""
        ok = await self.db.connect()
        if not ok:
            raise RuntimeError(f"Failed to connect to store '{self.store_name}'.")
        base = getattr(self.db, "_Base", None)
        if not base or not hasattr(base, "classes"):
            raise AttributeError("Automap Base/classes not initialized on Database after connect().")

        if not hasattr(base.classes, self.model_name):
            available = [n for n in dir(base.classes) if not n.startswith("_")]
            raise AttributeError(
                f"Model '{self.model_name}' not found in db._Base.classes. "
                f"Available: {sorted(available)}"
            )
        self.model = getattr(base.classes, self.model_name)

    # ---------- CRUD (requires connect() first) ----------

    def _require_model(self):
        if self.model is None:
            raise RuntimeError("Repo not connected. Call `await repo.connect()` before using CRUD.")

    async def all(self) -> list[Any]:
        from sqlalchemy import select
        self._require_model()
        async with self.db.session() as session:
            result = await session.execute(select(self.model))
            return list(result.scalars().all())

    async def get(self, id: Any) -> Optional[Any]:
        self._require_model()
        async with self.db.session() as session:
            return await session.get(self.model, id)

    async def find(self, **filters: Any) -> list[Any]:
        from sqlalchemy import select
        self._require_model()
        async with self.db.session() as session:
            stmt = select(self.model).filter_by(**filters)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def create(self, **fields: Any) -> Any:
        self._require_model()
        async with self.db.session() as session:
            async with session.begin():
                obj = self.model(**fields)
                session.add(obj)
            await session.refresh(obj)
            return obj

    async def update(self, id: Any, **fields: Any) -> Optional[Any]:
        self._require_model()
        async with self.db.session() as session:
            async with session.begin():
                obj = await session.get(self.model, id)
                if not obj:
                    return None
                for k, v in fields.items():
                    setattr(obj, k, v)
            await session.refresh(obj)
            return obj

    async def delete(self, id: Any) -> bool:
        self._require_model()
        async with self.db.session() as session:
            async with session.begin():
                obj = await session.get(self.model, id)
                if not obj:
                    return False
                await session.delete(obj)
            return True

    async def create_many(self, rows: Sequence[dict[str, Any]]) -> list[Any]:
        self._require_model()
        async with self.db.session() as session:
            async with session.begin():
                objs = [self.model(**row) for row in rows]
                session.add_all(objs)
            for obj in objs:
                await session.refresh(obj)
            return objs
