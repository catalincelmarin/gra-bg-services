import json
import os

import yaml



class DBFactory:
    _instances = {}
    @classmethod
    def get_db(cls, connection_name,uri=None,**kwargs):
        if connection_name not in cls._instances and uri is not None:
            cls._instances[connection_name] = Database(uri=uri, connection_name=connection_name)
        return cls._instances[connection_name]

    @classmethod
    def close_db(cls, connection_name):
        if connection_name in cls._instances:
            store = cls._instances.pop(connection_name)
            store.close()

    @staticmethod
    def load_dbs(dbs_path: str):
        pth = f"{dbs_path}/app"

        for root, dirs, files in os.walk(pth):
            for filename in files:
                if filename.startswith("dbs") and filename.endswith("yaml"):
                    file_path = os.path.join(root, filename)  # ✅ FIXED path

                    if os.path.isfile(file_path):
                        with open(file_path, "r") as file:
                            file_content = yaml.safe_load(file) or {}
                            more_dbs = file_content.get("dbs", [])

                            if more_dbs:
                                from kimera.db.Database import Database  # ✅ Optional: put import at top if repeated

                            for db in more_dbs:
                                t_uri = db.get("uri")
                                if t_uri:
                                    uri = os.getenv(t_uri)
                                    DBFactory.get_db(connection_name=db["name"], uri=uri)
                                else:
                                    print(f"NO URI : {json.dumps(db)}")