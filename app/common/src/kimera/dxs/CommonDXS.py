import json
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from abc import abstractmethod
from .BaseDXS import BaseDXS


class CommonDXS(BaseDXS):
    def __init__(self, method_config):
        super().__init__(method_config=method_config)
        default_routes = [
                      {
                        "path": "/",
                        "action": "init",
                        "method": "GET"
                      }
                    ]

        method_config["routes"] = [] if "routes" not in method_config.keys() else method_config["routes"]
        if method_config["resource"] is not False:
            self._routes = [*default_routes,*(method_config["routes"] if method_config["routes"] is not None else [])]
        else:
            self._routes = method_config["routes"]


    # @abstractmethod
    # async def init(self):
    #     pass
