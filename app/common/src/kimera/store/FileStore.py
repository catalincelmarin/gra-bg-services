class LocalFileStore:
    def __init__(self, path, **kwargs):
        self._path = path
        self._base_path = path

    def path(self, route = "/"):
        return f"{self._path}{route}"

    def base_path(self, route = "/"):
        return f"{self._base_path}{route}"

