from abc import abstractmethod, ABC
from urllib.parse import urlencode

import requests

from kimera.helpers.Helpers import Helpers


class Hook(ABC):
    def __init__(self, url: str, method: str,auth:None):
        self.url = url
        self.method = method
        self.auth = auth
        self.auth_resolve = None

    def __call__(self, data:dict | None):

        headers = {
            "Content-Type": "application/json"  # Adjust content type if needed
        }
        url = self.url
        if self.auth is not None:
            if self.auth["type"] == "Bearer" and self.auth_resolve is None:
                response = requests.post(self.auth["url"], json=self.auth["auth"])

                if response.status_code == 200:

                    if response.headers.get("Content-Type") == "application/json":
                        try:
                            self.auth_resolve = response.json()[self.auth["extract"]]
                        except Exception as e:
                            Helpers.sysPrint("HOOK_AUTH",e)
                    else:
                        self.auth_resolve = response.text

        if self.auth_resolve is not None and self.auth["type"] == "Bearer":
            headers["Authorization"] = f"Bearer {self.auth_resolve}"

        if data is not None:
            url = f"{url}?{urlencode(data)}"

        if self.method.upper() == "GET":

            response = requests.get(url,headers=headers)

            # Checking response status code
            if response.status_code == 200:
                if response.headers.get("Content-Type") == "application/json":
                    return response.json()
                else:
                    return response.text
            else:
                return response.status_code
        elif self.method.upper() == "POST":
            if data is None:
                data = {"data":None}

            response = requests.post(url, json=data,headers=headers)

            # Checking response status code
            if response.status_code == 200:
                if response.headers.get("Content-Type") == "application/json":
                    return response.json()
                else:
                    return response.text
            else:
                return response.status_code

    @abstractmethod
    def run(self, result):
        pass