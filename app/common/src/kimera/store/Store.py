import os

from mongoengine import connect

from kimera.helpers.Helpers import Helpers
from pymongo import MongoClient
from urllib.parse import quote_plus


class Store:
    def __init__(self, uri=None, connection_name='default', **kwargs):
        end = uri.split("@").pop()
        protocol = uri.split("://")[0]
        if len(uri.split("@")) > 1:
            start = ":".join([quote_plus(item) for item in "".join("".join(uri.split("@")[:-1]).split("//")[1:]).split(":")])
            self.uri = f"{protocol}://{start}@{end}"
        else:
            self.uri = uri

        self.pool_size = 50
        self.client = None
        self.db = self.uri.split("/")[-1:][0]
        self._connected = False

        self.connection_name=connection_name

        self.client = MongoClient(
            self.uri,
            maxPoolSize=self.pool_size,
            waitQueueMultiple=10,
            waitQueueTimeoutMS=10000,
            connect=False
        )

        if connection_name != '_root':
            self.connect(self.db)


    def connect(self, db=None):
        try:
            if self.client:
                # Create a MongoClient instance with connection pooling

                if db is None:
                    db = self.uri.split("/")[-1:][0]

                self.db = self.client.get_database(db)
                self._connected = True

                connect(host=self.uri, alias=self.connection_name,db=db)

        except Exception as e:
            # Connection failed
            Helpers.errPrint(e,os.path.basename(__file__))
        finally:
            return self._connected

    def get_databases(self):
        return self.client.list_database_names()

    def close(self):
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB")

    def use(self, collection=None):
        return self.db.get_collection(collection)
