from abc import ABC

class BaseDXS(ABC):
    def __init__(self, method_config):
        self.base_space = method_config["baseSpace"]
        self.url_space = method_config["urlSpace"]
        self.token = None
        method_config["routes"] = [] if "routes" not in method_config.keys() else method_config["routes"]

        self._routes = method_config["routes"]

    @property
    def path(self):
        return f"/{self.url_space}"

    @property
    def routes(self):
        return self._routes
