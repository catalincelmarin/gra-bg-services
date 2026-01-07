import os
import asyncio

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_scoped_session
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData, inspect, text

from kimera.helpers.Helpers import Helpers


class Database:
    def __init__(self, uri=None, connection_name='default', **kwargs):
        self.uri = uri
        self.connection_name = connection_name

        self._engine = None
        self._session = None
        self._metadata = None
        self._Base = None
        self._inspector = None
        self._connected = False

    async def connect(self, db=None):
        try:
            if db:
                parts = self.uri.split("/")
                if len(parts) > 3:
                    parts[3] = db
                    self.uri = "/".join(parts)
                else:
                    self.uri += f"/{db}"
            self._engine = create_async_engine(
                self.uri,
                pool_size=50,
                max_overflow=10,
                future=True,
                echo=False
            )

            async with self._engine.begin() as conn:
                # Prepare metadata, automap, and inspector
                await conn.run_sync(self._sync_reflection)

                # Test connection
                result = await conn.execute(text("SELECT 1"))
                if result.scalar() == 1:
                    self._connected = True
                else:
                    Helpers.infoPrint(f"Failed to connect to {self.connection_name} database")

            session_factory = sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            self._session = async_scoped_session(session_factory, scopefunc=asyncio.current_task)

        except Exception as e:
            Helpers.errPrint(e, os.path.basename(__file__))
        return self._connected

    def _sync_reflection(self, sync_conn):
        metadata = MetaData()
        metadata.reflect(bind=sync_conn)

        Base = automap_base(metadata=metadata)
        Base.prepare()

        self._metadata = metadata
        self._Base = Base
        self._inspector = inspect(sync_conn)

    async def exec(self, sql: str):
        async with self._engine.begin() as conn:
            try:
                result = await conn.execute(text(sql))
                return result
            except Exception as e:
                return f"{self.uri} {e}"

    async def switch_db(self, db_name: str):
        try:
            if self._connected:
                await self.close()

            if "?" in self.uri:
                base_uri = self.uri.split("/")[0] + "//" + self.uri.split("/")[2]
                new_uri = f"{base_uri}/{db_name}?" + self.uri.split("?")[1]
            else:
                base_uri = self.uri.split("/")[0] + "//" + self.uri.split("/")[2]
                new_uri = f"{base_uri}/{db_name}"

            Helpers.infoPrint(f"Switching to database: {db_name}")
            self.uri = new_uri
            await self.connect()

        except Exception as e:
            Helpers.errPrint(f"Error switching to new database: {str(e)}", os.path.basename(__file__))

    async def create(self, db: str):
        try:
            if not self._engine:
                await self.connect()

            async with self._engine.begin() as conn:
                await conn.execute(text(f"CREATE DATABASE {db};"))
        except Exception as e:
            Helpers.errPrint(f"Error creating database {db}: {str(e)}", os.path.basename(__file__))
            return e

        return True

    async def close(self):
        if self._engine:
            await self._engine.dispose()

    @property
    def session(self):
        return self._session
