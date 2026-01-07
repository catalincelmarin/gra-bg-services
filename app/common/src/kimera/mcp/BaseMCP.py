import os
from abc import ABC, abstractmethod
from typing import Dict, Any

import yaml
from kimera.helpers.Helpers import Helpers


class BaseMCP(ABC):
    def __init__(self,server_config,tools_config=None,prompts_config=None,resources_config=None):
        self.base_space = server_config["baseSpace"]
        self.url_space = server_config["urlSpace"]
        self.token = None
        self._server_config = server_config.get("server-config",{})
        default_routes = [
            {"path": "/", "action": "on_root", "method": "POST"},
        ]

        folder_path = tools_config.get("dir")

        tools_config = []
        for f_name in os.listdir(folder_path):
            if f_name.startswith("tools."):
                full_path = os.path.join(folder_path, f_name)
                with open(full_path) as file:
                    tools_config = [*tools_config, *yaml.safe_load(file).get("tools", [])]

        folder_path = prompts_config.get("dir")

        prompts_config = []
        for f_name in os.listdir(folder_path):
            if f_name.startswith("prompts."):
                full_path = os.path.join(folder_path, f_name)
                with open(full_path) as file:
                    prompts_config = [*prompts_config, *yaml.safe_load(file).get("prompts", [])]

        folder_path = resources_config.get("dir")

        resources_config = []
        for f_name in os.listdir(folder_path):
            if f_name.startswith("resources."):
                full_path = os.path.join(folder_path, f_name)
                with open(full_path) as file:
                    resources_config = [*resources_config, *yaml.safe_load(file).get("resources", [])]
        

        self._tools_config = tools_config
        self._prompts_config = prompts_config
        self._resources_config = resources_config
        self._default_routes = default_routes
        self._bounded_tools = {}
        self._bounded_prompts = {}
        self._bounded_resources = {}

        if tools_config:
            for tool in tools_config:
                self._bounded_tools[tool.get("definition").get("name")] = tool.get("call", "default_call")

        if prompts_config:
            for prompt in prompts_config:
                if prompt.get("call"):
                    self._bounded_prompts[prompt.get("definition").get("name")] = prompt.get("call")
                else:
                    Helpers.warnPrint(f"{prompt.get('definition').get('name')} is missing a bounded prompt method")

        if resources_config:
            for resource in resources_config:
                if resource.get("call"):
                    self._bounded_resources[resource.get("definition").get("uri")] = resource.get("call")
                else:
                    Helpers.warnPrint(f"{resource.get('definition').get('name')} is missing a bounded resource method")

        


    @property
    def path(self):
        return f"/{self.url_space}"

    @property
    def routes(self):
        return self._default_routes

    # ---- Abstract hooks every MCP server must implement ----
    @property
    def server_config(self) -> dict:  # { name, version }
        return self._server_config

    @abstractmethod
    async def initialize(self,body: Dict[str, Any] | None = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def tools_list(self, body: Dict[str, Any] | None = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def prompts_list(self, body: Dict[str, Any] | None = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def resources_list(self, body: Dict[str, Any] | None = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def tools_call(self, body: Dict[str, Any] | None = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def resources_read(self, body: Dict[str, Any] | None = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def on_root(self,body: Dict[str, Any] | None = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def default_call(self,*args,**kwargs):
        pass
