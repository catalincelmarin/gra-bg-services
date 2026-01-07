import importlib
from fastapi import HTTPException

from fastapi import Depends
from pydantic import ValidationError

from .BaseDXS import BaseDXS
from ..comm.JWTAuth import JWTAuth

auth = JWTAuth()

class ResourceDXS(BaseDXS):
    def __init__(self, method_config):
        super().__init__(method_config)
        self.repo = None

        default_routes = [
            {"path": "/", "action": "find", "method": "GET"},
            {"path": "/{id}", "action": "findOne", "method": "GET"},
            {"path": "/", "action": "create", "method": "POST"},
            {"path": "/{id}", "action": "update", "method": "PUT"},
            {"path": "/{id}", "action": "delete", "method": "DELETE"}
        ]

        if method_config["resource"] is not False and "repo" in method_config:
            module = importlib.import_module(method_config["repo"])
            self.repo = getattr(module, method_config["repo"].split(".")[-1:][0])()
            self._routes = [*default_routes, *self._routes]


    async def create(self, data: dict):
        if self.repo is not None:
            try:
                # Create an instance of the Item model using the incoming data
                item = self.repo.schema_cls(**data)
                # Validate the instance against the Item schema
                item_dict = item.dict()
            except ValidationError as e:
                # If a ValidationError occurs, extract the error details
                error_messages = []
                for error in e.errors():
                    error_messages.append({
                        "loc": error["loc"],
                        "msg": error["msg"],
                        "type": error["type"]
                    })

                # Return a nicely formatted error response
                raise HTTPException(status_code=422, detail=error_messages)
            else:
                # If validation is successful, proceed with your logic

                new_data = self.repo.create(data)
                return {"data":new_data}
        else:
            raise NotImplementedError(f"Method '{self.create.__name__}' must be implemented by a subclass.")

    async def delete(self, id: str, token=Depends(auth.get_auth)):
        if self.repo is not None:
            result = self.repo.delete(id)
            return {"data": result}
        else:
            raise NotImplementedError(f"Method '{self.delete.__name__}' must be implemented by a subclass.")

    async def find(self, token=Depends(auth.get_auth)):
        if self.repo is not None:
            result = self.repo.all()
            for item in result:
                if "password" in item.keys():
                    del item["password"]
            return {"data": result}
        else:
            raise NotImplementedError(f"Method '{self.find.__name__}' must be implemented by a subclass.")

    async def findOne(self, id: str, token=Depends(auth.get_auth)):
        if self.repo is not None:
            result = self.repo.one(id)
            if "password" in result.keys():
                del result["password"]

            return {"data": result}
        else:
            raise NotImplementedError(f"Method '{self.findOne.__name__}' must be implemented by a subclass.")

    async def update(self, id: str, data: dict, token=Depends(auth.get_auth)):
        if self.repo is not None:
            result = self.repo.update(id, data)
            return {"data": result}
        else:
            raise NotImplementedError(f"Method '{self.update.__name__}' must be implemented by a subclass.")
